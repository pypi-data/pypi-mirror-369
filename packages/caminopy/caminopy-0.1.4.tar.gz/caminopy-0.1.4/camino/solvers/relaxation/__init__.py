# This file is part of CAMINO
# Copyright (C) 2024  Andrea Ghezzi, Wim Van Roy, Sebastian Sager, Moritz Diehl
# SPDX-License-Identifier: GPL-3.0-or-later

"""A set of solvers that compute relaxed solutions (non-integer feasible)."""

import logging
from camino.data import MinlpData
from camino.solvers import MiSolverClass
from camino.solvers.subsolvers.nlp import NlpSolver as SubSolver
from camino.utils import colored
from camino.utils.validate import check_integer_feasible

logger = logging.getLogger(__name__)


class NlpSolver(MiSolverClass):

    def __init__(self, problem, data, stats, settings, integers_relaxed=False):
        super(NlpSolver, self).__init__(problem, data, stats, settings)
        self.nlp = SubSolver(problem, stats, settings)
        self.integers_relaxed = integers_relaxed

    def solve(self, nlpdata: MinlpData) -> MinlpData:
        nlpdata = self.nlp.solve(nlpdata, integers_relaxed=self.integers_relaxed)
        nlpdata.relaxed = check_integer_feasible(
            self.nlp.idx_x_integer, nlpdata.x_sol, self.settings, throws=False
        )
        if self.integers_relaxed:
            self.stats.relaxed_solution = nlpdata
        return nlpdata

    def reset(self, nlpdata: MinlpData):
        logger.warning(colored("Nothing to reset for RelaxedNlpSolver"))

    def warmstart(self, nlpdata: MinlpData):
        pass
