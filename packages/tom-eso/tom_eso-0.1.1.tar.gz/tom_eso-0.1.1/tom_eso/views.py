import logging
# from django.shortcuts import render
from django.http import HttpResponse

from crispy_forms.templatetags.crispy_forms_filters import as_crispy_field

from tom_eso.eso_api import ESOAPI
from tom_eso.eso import ESOObservationForm, ESOFacility

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def folders_for_observing_run(request):
    """Return an HTTPResponse which updates the Folder choices for the selected Observing Run.

    Calls to this View are triggered by a change of the ``p2_observing_run`` ChoiceField,
    as specified by the htmx attributes on its <select> element. See the ESOFacility,
    where that ChoiceField is defined.

    The ``p2_folder_name`` ChoiceField's ``choices`` are updated with the folder names
    for the selected Observing Run.  and the <select> element is returned as an
    <select> HTML element. Function view for the htmx GET request to update the observing run field.

    The ``observing_run_id`` of the selected ``p2_observing_run`` is passed as a URL
    parameter and is thus available from the request.GET QueryDict.
    """
    # extract the observing run id from the request.GET QueryDict
    observing_run_id = int(request.GET['p2_observing_run'])

    # Get the folder name choices for the selected observing run
    # NOTE: this is a potentially slow API call
    # TODO: considing caching the results
    folder_name_choices = ESOAPI().folder_name_choices(observing_run_id)

    form = ESOObservationForm()  # instantiate the UNBOUND form
    form.fields['p2_folder_name'].choices = folder_name_choices  # update the choices of the UNBOUND form

    # get the HTML for the updated ChoiceField that will update the p2_folder_name in the DOM
    field_html = as_crispy_field(form['p2_folder_name'])
    return HttpResponse(field_html)


def observation_blocks_for_folder(request):
    """Return an HTTPResponse which updates the Observation Blocks choices for the selected Folder.

    Calls to this View are triggered by a change of the ``p2_folder_name`` ChoiceField,
    as specified by the htmx attributes on its <select> element. See the ESOFacility,
    where that ChoiceField is defined.

    The ``folder_items`` MultipleChoiceField's ``choices`` are updated with the folder items
    for the selected Folder, and the <select> element is returned as an <select> HTML element.
    """
    # extract the folder id from the request.GET QueryDict
    try:
        folder_id = int(request.GET['p2_folder_name'])
    except ValueError as e:
        logger.error(f'folder_id is not an integer: {request.GET["p2_folder_name"]}')
        for key, value in request.GET.items():
            logger.error(f'{key}: {value}')
        folder_id = 0
        raise e  # re-raise the exception

    # Get the observation_blocks in the selected folder
    observation_block_choices = ESOAPI().folder_ob_choices(folder_id)

    form = ESOObservationForm()  # instantiate the UNBOUND form
    form.fields['observation_blocks'].choices = observation_block_choices  # update the choices of the UNBOUND form

    # now render the field as HTM and return it in the HTTPResponse
    field_html = as_crispy_field(form['observation_blocks'])
    return HttpResponse(field_html)


def show_observation_block(request):
    """When a new observation block is created, this View updates the ESO P2 tool iframe
    to show the new observation block.
    """
    # 1. extract the observation block id from the request.GET QueryDict
    # (this is the value associated with the choice in the MultipleChoiceField.choices)
    try:
        observation_block_id = int(request.GET['observation_blocks'])
    except ValueError as e:
        logger.error(f'ob_id is not an integer: {request.GET["observation_blocks"]}')
        for key, value in request.GET.items():
            logger.error(f'{key}: {value}')
        observation_block_id = 0
        raise e  # re-raise the exception

    # get the ESO P2 tool URL for this observation block
    iframe_url = ESOFacility().get_p2_tool_url(observation_block_id=observation_block_id)

    # replace the hx-target div with the iframe pointed to the new observation block
    html = (f'<div id="div_id_eso_p2_tool_iframe" style="height:800px;">'
            f'<iframe id="id_eso_p2_tool_iframe" height=100% width="100%" src="{iframe_url}">'
            f'</iframe></div>')
    return HttpResponse(html)
