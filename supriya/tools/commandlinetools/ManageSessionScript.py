# -*- encoding: utf-8 -*-
from supriya.tools.commandlinetools.ProjectSectionScript import (
    ProjectSectionScript
)


class ManageSessionScript(ProjectSectionScript):
    '''
    Manages project package sessions.

    ..  shell::

        sjv session --help

    '''

    ### CLASS VARIABLES ###

    alias = 'session'
    short_description = 'manage project package sessions'

    ### PRIVATE PROPERTIES ###

    @property
    def _section_plural(self):
        return 'sessions'

    @property
    def _section_singular(self):
        return 'session'
