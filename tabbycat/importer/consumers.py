from statistics import mean
from xml.etree import ElementTree

from channels.consumer import SyncConsumer
from django.utils.text import slugify

from adjallocation.models import DebateAdjudicator
from adjfeedback.models import AdjudicatorFeedback, AdjudicatorFeedbackQuestion
from breakqual.models import BreakCategory
from draw.models import Debate, DebateTeam
from motions.models import Motion
from participants.emoji import EMOJI_BY_NAME
from participants.models import Adjudicator, Institution, Region, Speaker, SpeakerCategory, Team
from results.models import BallotSubmission, SpeakerScore, SpeakerScoreByAdj, Submission, TeamScore
from tournaments.models import Round, Tournament
from venues.models import Venue


class ImportArchiveConsumer(SyncConsumer):

    def import_tournament(self, data):
        self.root = ElementTree.fromstring(data)

        self.tournament = Tournament(
            name=self.root.get('name'), short_name=self.root.get('name')[:25],
            slug=slugify(self.root.get('name')[:50]))
        self.tournament.save()

        self.is_bp = len(self.root.find('round').find('debate').findall('side')) == 4

        # Import all the separate parts
        self.import_institutions()
        self.import_categories()
        self.import_venues()
        self.import_questions()
        self.import_teams()
        self.import_speakers()
        self.import_adjudicators()
        self.import_debates()
        self.import_motions()
        self.import_results()
        self.import_feedback()

    def import_institutions(self):
        self.institutions = {}
        self.regions = {}

        for institution in self.root.findall('institution'):
            # Use get_or_create as institutions may be shared between tournaments
            inst_obj, created = Institution.objects.get_or_create(
                code=institution.get('reference'), name=institution.text
            )
            self.institutions[institution.get('id')] = inst_obj

            if institution.get('region') is not None:
                region = institution.get('region')
                if region not in self.regions:
                    self.regions[region] = Region.objects.get_or_create(name=region)

                inst_obj.region = self.regions[region]
                inst_obj.save()

    def import_categories(self):
        self.team_breaks = {}
        self.speaker_categories = {}

        for i, breakqual in enumerate(self.root.findall('break-category'), 1):
            self.team_breaks[breakqual.get('id')] = BreakCategory(
                tournament=self.tournament, name=breakqual.text,
                slug=slugify(breakqual.text[:50]), seq=i,
                break_size=0, is_general=False, priority=0
            )
        BreakCategory.objects.bulk_create(self.team_breaks.values())

        for i, category in enumerate(self.root.findall('speaker-category'), 1):
            self.speaker_categories[category.get('id')] = SpeakerCategory(
                tournament=self.tournament, name=category.text,
                slug=slugify(category.text[:50]), seq=i
            )
        SpeakerCategory.objects.bulk_create(self.speaker_categories.values())

    def import_venues(self):
        self.venues = {}

        for venue in self.root.findall('venue'):
            self.venues[venue.get('id')] = Venue(tournament=self.tournament, name=venue.text, priority=0)
        Venue.objects.bulk_create(self.venues.values())

    def import_questions(self):
        self.questions = {}

        for i, question in enumerate(self.root.findall('question'), 1):
            self.questions[question.get('id')] = AdjudicatorFeedbackQuestion(
                tournament=self.tournament, seq=i, text=question.text,
                name=question.get('name'), reference=slugify(question.get('name')[:50]),
                from_adj=question.attrib['from-adjudicators'], from_team=question.get('from-teams'),
                answer_type=question.get('type'), required=False
            )
        AdjudicatorFeedbackQuestion.objects.bulk_create(self.questions.values())

    def _add_foreign_key(self, tupl, foreign):
        elements = []
        for element, key in tupl:
            elements.append(element)
            setattr(element, foreign, key)
        return elements

    def import_teams(self):
        self.teams = {}

        through_model = Team.break_categories.through
        team_categories = []

        for team in self.root.find('participants').findall('team'):
            team_obj = Team(tournament=self.tournament, long_name=team.get('name'))
            self.teams[team.get('id')] = team_obj

            # Get emoji & code name
            if 'code' in team.attrib:
                team_obj.code_name = team.get('code')
            emoji = EMOJI_BY_NAME.get(team.get('code'))
            if emoji is not None:
                team_obj.emoji = emoji

            # Find institution from speakers
            p_institutions = set([p.get('institution') for p in team.findall('speaker')])
            team_institution = list(p_institutions)[0]

            if len(p_institutions) == 1 and team_institution is not None:
                team_obj.institution = self.institutions[team_institution]

            # Remove institution from team name
            if team_obj.institution is not None and team_obj.long_name.startswith(team_obj.institution.name + " "):
                team_obj.reference = team_obj.long_name[len(team_obj.institution.name) + 1:]
                team_obj.short_name = team_obj.institution.code + " " + team_obj.reference
                team_obj.use_institution_prefix = True
            else:
                team_obj.reference = team_obj.long_name
                team_obj.short_name = team_obj.reference[:50]
            team_obj.short_reference = team_obj.reference[:35]

            # Break eligibilities
            for bc in team.get('break-eligibilities').split():
                team_categories.append((through_model(breakcategory=self.team_breaks[bc]), team_obj))

        Team.objects.bulk_create(self.teams.values())

        through_model.objects.bulk_create(self._add_foreign_key(team_categories, 'team'))

    def import_speakers(self):
        self.speakers = {}

        through_model = Speaker.categories.through
        categories = []

        for team in self.root.find('participants').findall('team'):
            for speaker in team.findall('speaker'):
                speaker_obj = Speaker(team=self.teams[team.get('id')], name=speaker.text, gender=speaker.get('gender', ''))
                speaker_obj.save()
                self.speakers[speaker.get('id')] = speaker_obj

                for sc in speaker.get('categories').split():
                    categories.append((through_model(speakercategory=self.speaker_categories[sc]), speaker_obj))

        through_model.objects.bulk_create(self._add_foreign_key(categories, 'speaker'))

    def import_adjudicators(self):
        self.adjudicators = {}

        for adj in self.root.find('participants').findall('adjudicator'):
            adj_obj = Adjudicator(
                tournament=self.tournament, test_score=adj.get('score', 0),
                institution=self.institutions.get(adj.get('institution')),
                independent=adj.get('independent'), adj_core=adj.get('core'),
                name=adj.get('name'), gender=adj.get('gender', ''))
            adj_obj.save()
            self.adjudicators[adj.get('id')] = adj_obj

    def _get_voting_adjs(self, debate):
        voting_adjs = set()
        for ballot in debate.findall('.//ballot'):
            voting_adjs.update(ballot.get('adjudicators').split())
        return voting_adjs

    def import_debates(self):
        self.debates = {}
        debates_rounds = []

        self.debateteams = {}
        debateteams_debates = []
        self.debateadjudicators = {}
        debateadjudicators_debates = []

        rounds = []
        for i, round in enumerate(self.root.findall('round'), 1):
            round_stage = Round.STAGE_ELIMINATION if round.get('elimination', 'False') == 'True' else Round.STAGE_PRELIMINARY
            draw_type = Round.DRAW_ELIMINATION if round_stage == Round.STAGE_ELIMINATION else Round.DRAW_MANUAL

            round_obj = Round(
                tournament=self.tournament, seq=i, completed=True, name=round.get('name'),
                abbreviation=round.get('name')[:10], stage=round_stage, draw_type=draw_type,
                draw_status=Round.STATUS_RELEASED, feedback_weight=round.get('feedback-weight'),
                starts_at=round.get('start')
            )
            rounds.append(round_obj)

            if round_stage == Round.STAGE_ELIMINATION:
                round_obj.break_category = self.team_breaks.get(round.get('break-category'))

            side_start = 2 if self.is_bp else 0

            for debate in round.findall('debate'):
                debate_obj = Debate(venue=self.venues.get(debate.get('venue')), result_status=Debate.STATUS_CONFIRMED)
                self.debates[debate.get('id')] = debate_obj
                debates_rounds.append((debate_obj, round_obj))

                # Debate-teams
                for i, side in enumerate(debate.findall('side'), side_start):
                    position = DebateTeam.SIDE_CHOICES[i][0]
                    debateteam_obj = DebateTeam(team=self.teams[side.get('team')], side=position)
                    self.debateteams[(debate.get('id'), side.get('team'))] = debateteam_obj
                    debateteams_debates.append((debateteam_obj, debate_obj))

                # Debate-adjudicators
                voting_adjs = self._get_voting_adjs(debate)
                for adj in debate.get('adjudicators').split():
                    adj_type = DebateAdjudicator.TYPE_PANEL if adj in voting_adjs else DebateAdjudicator.TYPE_TRAINEE
                    if debate.get('chair') == adj:
                        adj_type = DebateAdjudicator.TYPE_CHAIR
                    adj_obj = DebateAdjudicator(adjudicator=self.adjudicators[adj], type=adj_type)
                    self.debateadjudicators[(debate.get('id'), adj)] = adj_obj
                    debateadjudicators_debates.append((adj_obj, debate_obj))

        Round.objects.bulk_create(rounds)
        Debate.objects.bulk_create(self._add_foreign_key(debates_rounds, 'round'))
        DebateTeam.objects.bulk_create(self._add_foreign_key(debateteams_debates, 'debate'))
        DebateAdjudicator.objects.bulk_create(self._add_foreign_key(debateadjudicators_debates, 'debate'))

    def import_motions(self):
        # Can cause data consistency problems if motions are re-used between rounds: See #645
        self.motions = {}

        motions_by_round = {}
        seq_by_round = {}
        for r_obj, round in zip(self.tournament.round_set.all().order_by('seq'), self.root.findall('round')):
            motions_by_round[r_obj.id] = set()
            seq_by_round[r_obj.id] = 1
            for debate in round.findall('debate'):
                motions_by_round[r_obj.id].add(debate.get('motion'))

        for motion in self.root.findall('motion'):
            for r, m_set in motions_by_round.items():
                if motion.get('id') in m_set:
                    motion_obj = Motion(
                        seq=seq_by_round[r], text=motion.text, reference=motion.get('reference'),
                        info_slide=getattr(motion.find('info-slide'), 'text', ''), round_id=r
                    )
                    self.motions[motion.get('id')] = motion_obj
        Motion.objects.bulk_create(self.motions.values())

    def _get_margin(self, debate):
        side_ts = []
        for side in debate.findall('side'):
            scores = []
            for b in side.findall("ballot[@ignored='False']"):
                try:
                    scores.append(float(b.text))
                except ValueError:
                    continue
            side_ts.append(mean(scores))
        return (max(side_ts), max(side_ts) - min(side_ts))

    def _is_consensus(self, round):
        if self.is_bp:
            return True
        for d in round.findall('debate'):
            adjs = d.get('adjudicators').split()
            if adjs == d.get('adjudicators'):
                continue # Only one adj
            if len(d.findall('side/ballot')) != 2:
                return False
        return True

    def _get_adj_split(self, debate, numeric):
        split = [0, 0, 0, 0]
        side_ballot_by_adj = {adj: [] for adj in self._get_voting_adjs(debate)}
        for side in debate.findall('side'):
            for ballot in side.findall('ballot'):
                for adj in ballot.get('adjudicators').split():
                    if numeric:
                        side_ballot_by_adj[adj] = float(ballot.text)
                    else:
                        side_ballot_by_adj[adj] = int(ballot.text == 'True')
        for adj, scores in side_ballot_by_adj.items():
            max_score = max(scores)
            for i, score in enumerate(split):
                if score == max_score:
                    split[i] += 1
        return (split, len(side_ballot_by_adj))

    def import_results(self):
        ballotsubmissions = []
        teamscores = []
        speakerscores = []
        speakerscores_adj = []

        for round in self.root.findall('round'):
            consensus = self._is_consensus(round)

            for debate in round.findall('debate'):
                bs_obj = BallotSubmission(
                    version=1, submitter_type=Submission.SUBMITTER_TABROOM, confirmed=True,
                    debate=self.debates[debate.get('id')], motion=self.motions.get(debate.get('motion'))
                )
                ballotsubmissions.append(bs_obj)

                ts_max, ts_margin = (0, 0)
                numeric_scores = True
                try:
                    float(debate.find("side/ballot[@ignored='False']").text)
                except ValueError:
                    numeric_scores = False

                if not self.is_bp and numeric_scores:
                    ts_max, ts_margin = self._get_margin(debate)

                adj_split, num_adjs = (None, None)
                if not consensus:
                    adj_split, num_adjs = self._get_adj_split(debate, numeric_scores)

                for i, side in enumerate(debate.findall('side')):
                    dt = self.debateteams.get((debate.get('id'), side.get('team')))

                    team_ballot = side.find("ballot[@ignored='False']")
                    points = 4 - int(team_ballot.get('rank')) if self.is_bp else 2 - int(team_ballot.get('rank'))

                    not_ignored = side.findall("ballot[@ignored='False']")

                    ts_obj = TeamScore(debate_team=dt, points=points)
                    teamscores.append((ts_obj, bs_obj))

                    if not self.is_bp:
                        ts_obj.win = points == 1

                    if numeric_scores:
                        scores = []
                        for b in not_ignored:
                            try:
                                scores.append(float(b.text))
                            except ValueError:
                                continue
                        ts_obj.score = mean(scores)
                        if not self.is_bp:
                            ts_obj.margin = ts_margin if float(team_ballot.text) == ts_max else -ts_margin
                    else:
                        ts_obj.win = team_ballot.text # Boolean for advancing otherwise

                    if consensus:
                        ts_obj.votes_given = 1 if ts_obj.win else 0
                        ts_obj.votes_possible = 1
                    else:
                        ts_obj.votes_given = adj_split[i]
                        ts_obj.votes_possible = num_adjs

                    for i, speech in enumerate(side.findall('speech'), 1):
                        ss_obj = None
                        if consensus:
                            speech_ballot = speech.find('ballot')

                            ss_obj = SpeakerScore(debate_team=dt, speaker=self.speakers[speech.get('speaker')],
                                score=float(speech_ballot.text), position=i)
                        else:
                            speech_ballots = speech.findall('ballot')
                            for speech_ballot in speech_ballots:
                                d_adj = self.debateadjudicators.get((debate.get('id'), speech_ballot.get('adjudicators')))
                                ss_adj_obj = SpeakerScoreByAdj(debate_adjudicator=d_adj,
                                    debate_team=dt, score=float(speech_ballot.text), position=i)
                                speakerscores_adj.append((ss_adj_obj, bs_obj))

                            included_adjs = [b.get('adjudicators') for b in not_ignored]
                            ss_obj = SpeakerScore(debate_team=dt, speaker=self.speakers[speech.get('speaker')], position=i,
                                score=mean([float(b.score) for b in speech_ballots if b.adjudicators in included_adjs])
                            )
                        speakerscores.append((ss_obj, bs_obj))

        BallotSubmission.objects.bulk_create(ballotsubmissions)

        TeamScore.objects.bulk_create(self._add_foreign_key(teamscores, 'ballot_submission'))
        SpeakerScore.objects.bulk_create(self._add_foreign_key(speakerscores, 'ballot_submission'))
        SpeakerScoreByAdj.objects.bulk_create(self._add_foreign_key(speakerscores_adj, 'ballot_submission'))

    def import_feedback(self):
        feedbacks = []

        answers = {q[0]: [] for q in AdjudicatorFeedbackQuestion.ANSWER_TYPE_CHOICES}

        for adj in self.root.findall('participants/adjudicator'):
            adj_obj = self.adjudicators[adj.get('id')]

            for feedback in adj.findall('feedback'):
                d_adj = self.debateadjudicators.get((feedback.get('debate'), feedback.get('source-adjudicator')))
                d_team = self.debateteams.get((feedback.get('debate'), feedback.get('source-team')))
                feedback_obj = AdjudicatorFeedback(adjudicator=adj_obj, score=feedback.get('score'), version=1,
                    source_adjudicator=d_adj, source_team=d_team,
                    submitter_type=Submission.SUBMITTER_TABROOM, confirmed=True)
                feedbacks.append(feedback_obj)

                for answer in feedback.findall('answer'):
                    question = self.questions[answer.get('question')]

                    cast_answer = answer.text
                    # if question.answer_type in AdjudicatorFeedbackQuestion.NUMERICAL_ANSWER_TYPES:
                    #     cast_answer = float(cast_answer)

                    answers[question.answer_type].append(
                        (AdjudicatorFeedbackQuestion.ANSWER_TYPE_CLASSES[question.answer_type](
                            question=question, answer=cast_answer), feedback_obj))

        AdjudicatorFeedback.objects.bulk_create(feedbacks)

        for ans_type, objects in answers.items():
            AdjudicatorFeedbackQuestion.ANSWER_TYPE_CLASSES[ans_type].objects.bulk_create(
                self._add_foreign_key(objects, 'feedback'))
