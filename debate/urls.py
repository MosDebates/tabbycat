from django.conf.urls import *

from django.core.urlresolvers import reverse

from debate import models as m

urlpatterns = patterns('debate.views',
    url(r'^admin/$', 'tournament_home', name='tournament_home'),
    url(r'^admin/results_status_update/$', 'results_status_update', name='results_status_update'),
    url(r'^admin/draw/$', 'draw_index', name='draw_index'),
    url(r'^admin/round/(?P<round_seq>\d+)/$', 'round_index', name='round_index'),

    url(r'^$', 'public_index', name='public_index'),
    url(r'^draw/$', 'public_draw', name='public_draw'),
    url(r'^draw/round/(?P<round_seq>\d+)/$', 'public_draw_by_round', name='public_draw_by_round'),
    url(r'^draw/all/$', 'public_all_draws', name='public_all_draws'),

    url(r'^admin/round/(?P<round_seq>\d+)/results/$', 'results', name='results'),
    url(r'^results/$', 'public_results_index', name='public_results_index'),
    url(r'^results/round/(?P<round_seq>\d+)/$', 'public_results', name='public_results'),
    url(r'^standings/$',    'public_team_standings', name='public_team_standings'),

    url(r'^team_speakers/(?P<team_id>\d+)/$', 'team_speakers', name='team_speakers'),

    url(r'^add_ballot/$', 'public_ballot_submit', name='public_ballot_submit'),
    url(r'^add_ballot/adjudicator/(?P<adj_id>\d+)/$', 'public_new_ballotset_id', name='public_new_ballotset'),
    url(r'^add_ballot/adjudicator/h/(?P<url_key>\w+)/$', 'public_new_ballotset_key', name='public_new_ballotset_key'),
    url(r'^add_feedback/$', 'public_feedback_submit', name='public_feedback_submit'),
    url(r'^add_feedback/team/(?P<source_id>\d+)/$', 'public_enter_feedback_id', {'source_type': m.Team}, name='public_enter_feedback_team'),
    url(r'^add_feedback/team/h/(?P<url_key>\w+)/$', 'public_enter_feedback_key', {'source_type': m.Team}, name='public_enter_feedback_team_key'),
    url(r'^add_feedback/adjudicator/(?P<source_id>\d+)/$', 'public_enter_feedback_id', {'source_type': m.Adjudicator}, name='public_enter_feedback_adjudicator'),
    url(r'^add_feedback/adjudicator/h/(?P<url_key>\w+)/$', 'public_enter_feedback_key', {'source_type': m.Adjudicator}, name='public_enter_feedback_adjudicator_key'),
    url(r'^toggle_postponed/$', 'toggle_postponed', name='toggle_postponed'),

    url(r'^feedback_progress/$', 'public_feedback_progress', name='public_feedback_progress'),
    url(r'^participants/$', 'public_participants', name='public_participants'),
    url(r'^motions/$', 'public_motions', name='public_motions'),
    url(r'^divisions/$', 'public_divisions', name='public_divisions'),
    url(r'^side_allocations/$', 'public_side_allocations', name='public_side_allocations'),

    url(r'^ballots/debate/(?P<debate_id>\d+)/$', 'public_ballots_view', name='public_ballots_view'),

    #url(r'^admin/actions/$', 'action_log', name='action_log'),

    url(r'^admin/round/(?P<round_seq>\d+)/draw/$', 'draw', name='draw'),
    url(r'^admin/round/(?P<round_seq>\d+)/draw/details/$', 'draw_with_standings', name='draw_with_standings'),
    url(r'^admin/round/(?P<round_seq>\d+)/draw_display_by_venue/$', 'draw_display_by_venue', name='draw_display_by_venue'),
    url(r'^admin/round/(?P<round_seq>\d+)/draw_display_by_team/$', 'draw_display_by_team', name='draw_display_by_team'),
    url(r'^admin/round/(?P<round_seq>\d+)/draw/create/$', 'create_draw', name='create_draw'),
    url(r'^admin/round/(?P<round_seq>\d+)/draw/create_draw_with_all_teams/$', 'create_draw_with_all_teams', name='create_draw_with_all_teams'),
    url(r'^admin/round/(?P<round_seq>\d+)/draw/confirm/$', 'confirm_draw', name='confirm_draw'),
    url(r'^admin/round/(?P<round_seq>\d+)/draw/release/$', 'release_draw', name='release_draw'),
    url(r'^admin/round/(?P<round_seq>\d+)/draw/unrelease/$', 'unrelease_draw', name='unrelease_draw'),

    url(r'^admin/round/(?P<round_seq>\d+)/draw/matchups/edit/$', 'draw_matchups_edit', name='draw_matchups_edit'),
    url(r'^admin/round/(?P<round_seq>\d+)/draw/matchups/save/$', 'save_matchups', name='save_matchups'),

    url(r'^admin/round/(?P<round_seq>\d+)/draw/venues/$', 'draw_venues_edit', name='draw_venues_edit'),
    url(r'^admin/round/(?P<round_seq>\d+)/draw/venues/save/$', 'save_venues', name='save_venues'),

    url(r'^admin/round/(?P<round_seq>\d+)/draw/adjudicators/$', 'draw_adjudicators_edit', name='draw_adjudicators_edit'),
    url(r'^admin/round/(?P<round_seq>\d+)/draw/adjudicators/_get/$', 'draw_adjudicators_get', name='draw_adjudicators_get'),
    url(r'^admin/round/(?P<round_seq>\d+)/draw/adjudicators/save/$', 'save_adjudicators', name='save_adjudicators'),
    url(r'^admin/round/(?P<round_seq>\d+)/_update_importance/$', 'update_debate_importance', name='update_debate_importance'),


    url(r'^admin/round/(?P<round_seq>\d+)/round_increment_check/$', 'round_increment_check', name='round_increment_check'),
    url(r'^admin/round/(?P<round_seq>\d+)/round_increment/$', 'round_increment', name='round_increment'),

    url(r'^admin/round/(?P<round_seq>\d+)/adj_allocation/create/$', 'create_adj_allocation', name='create_adj_allocation'),


    url(r'^admin/round/(?P<round_seq>\d+)/start_time/set/$', 'set_round_start_time', name='set_round_start_time'),

    url(r'^admin/ballots/(?P<ballotsub_id>\d+)/edit/$', 'edit_ballotset', name='edit_ballotset'),
    url(r'^admin/debate/(?P<debate_id>\d+)/new_ballotset/$', 'new_ballotset', name='new_ballotset'),
    url(r'^admin/round/(?P<round_seq>\d+)/ballot_checkin/$', 'ballot_checkin', name='ballot_checkin'),
    url(r'^admin/round/(?P<round_seq>\d+)/ballot_checkin/get_details/$', 'ballot_checkin_get_details', name='ballot_checkin_get_details'),
    url(r'^admin/round/(?P<round_seq>\d+)/ballot_checkin/post/$', 'post_ballot_checkin', name='post_ballot_checkin'),

    url(r'^admin/round/(?P<round_seq>\d+)/adjudicators/conflicts/$', 'adj_conflicts', name='adj_conflicts'),
    url(r'^admin/round/(?P<round_seq>\d+)/master_sheets/list/$', 'master_sheets_list', name='master_sheets_list'),
    url(r'^admin/round/(?P<round_seq>\d+)/master_sheets/venue_group/(?P<venue_group_id>\d+)/$', 'master_sheets_view', name='master_sheets_view'),

    url(r'^admin/adjudicators/scores/$', 'adj_scores', name='adj_scores'),
    url(r'^admin/adjudicators/feedback/$', 'adj_feedback', name='adj_feedback'),
    url(r'^admin/adjudicators/feedback/latest/$', 'adj_latest_feedback', name='adj_latest_feedback'),
    url(r'^admin/adjudicators/feedback/source/list/$', 'adj_source_feedback', name='adj_source_feedback'),
    url(r'^admin/adjudicators/feedback/source/team/(?P<team_id>\d+)/$', 'team_feedback_list', name='team_feedback_list'),
    url(r'^admin/adjudicators/feedback/source/adjudicator(?P<adj_id>\d+)/$', 'adj_feedback_list', name='adj_feedback_list'),

    url(r'^admin/adjudicators/feedback/get/$', 'get_adj_feedback', name='get_adj_feedback'),
    url(r'^admin/adjudicators/feedback/add/$', 'add_feedback', name='add_feedback'),
    url(r'^admin/adjudicators/feedback/add/team/(?P<source_id>\d+)/$', 'enter_feedback', {'source_type': m.Team}, name='enter_feedback_team'),
    url(r'^admin/adjudicators/feedback/add/adjudicator/(?P<source_id>\d+)/$', 'enter_feedback', {'source_type': m.Adjudicator}, name='enter_feedback_adjudicator'),
    url(r'^admin/adjudicators/scores/test/set/$', 'set_adj_test_score', name='set_adj_test_score'),
    url(r'^admin/adjudicators/breaking/set/$', 'set_adj_breaking_status', name='set_adj_breaking_status'),
    url(r'^admin/adjudicators/notes/test/set/$', 'set_adj_note', name='set_adj_note'),

    url(r'^admin/adjudicators/progress$', 'feedback_progress', name='feedback_progress'),

    url(r'^admin/side_allocations/$', 'side_allocations', name='side_allocations'),
    url(r'^admin/randomised_urls/$', 'randomised_urls', name='randomised_urls'),
    url(r'^admin/randomised_urls/generate/$', 'generate_randomised_urls', name='generate_randomised_urls'),

    url(r'^admin/division_allocations/$', 'division_allocations', name='division_allocations'),
    url(r'^admin/division_allocations/save/$', 'save_divisions', name='save_divisions'),
    url(r'^admin/division_allocations/create/$', 'create_division_allocation', name='create_division_allocation'),

    url(r'^all_tournaments_all_venues/$', 'all_tournaments_all_venues', name='all_tournaments_all_venues'),
    url(r'^all_tournaments_all_venues/all_draws/(?P<venue_id>\d+)$', 'all_draws_for_venue', name='all_draws_for_venue'),
    url(r'^all_tournaments_all_institutions/$', 'all_tournaments_all_institutions', name='all_tournaments_all_institutions'),
    url(r'^all_tournaments_all_institutions/all_draws/(?P<institution_id>\d+)$', 'all_draws_for_institution', name='all_draws_for_institution'),
    url(r'^all_tournaments_all_teams/$', 'all_tournaments_all_teams', name='all_tournaments_all_teams'),

    # Printing App
    url(r'^admin/round/(?P<round_seq>\d+)/print/',          include('printing.urls')),

    # Standings App
    url(r'^tab/',                                           include('standings.urls_public')),
    url(r'^admin/round/(?P<round_seq>\d+)/standings/',      include('standings.urls_admin')),

    # Break App
    url(r'^break/',                                         include('breaking.urls_public')),
    url(r'^admin/break/',                                   include('breaking.urls_admin')),

    # Availability App
    url(r'^admin/round/(?P<round_seq>\d+)/availability/',   include('availability.urls')),

    # Motions App
    url(r'^admin/round/(?P<round_seq>\d+)/motions/',        include('motions.urls')),

    # Action Log App
    url(r'^admin/action_log/',                              include('action_log.urls')),

    # Config App
    url(r'^admin/options/',                                  include('options.urls')),

)