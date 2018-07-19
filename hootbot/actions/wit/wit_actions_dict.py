from hootbot.actions.wit import wit_actions
from hootbot.actions.facebook import facebook_actions

wit_actions_dict = {
    'get_started': facebook_actions.get_started_action,
    'change_network': facebook_actions.switch_networks_action,
    'done': facebook_actions.done_action,
    'support': wit_actions.assumed_support_request_action,
    'stop_tips': wit_actions.stop_tips_action,
    'Facebook': wit_actions.objectives_for_network_action,
    'Twitter': wit_actions.objectives_for_network_action,
    'Instagram': wit_actions.objectives_for_network_action,
    'LinkedIn': wit_actions.objectives_for_network_action,
    'YouTube': wit_actions.objectives_for_network_action,
    'Engaging Audience': wit_actions.networks_for_objective_action,
    'Sharing Content': wit_actions.networks_for_objective_action,
    'Advertising': wit_actions.networks_for_objective_action,
    'Proving ROI': wit_actions.networks_for_objective_action
}