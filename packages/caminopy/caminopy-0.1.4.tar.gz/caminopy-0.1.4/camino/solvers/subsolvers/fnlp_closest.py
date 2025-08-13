# This file is part of CAMINO
# Copyright (C) 2024  Andrea Ghezzi, Wim Van Roy, Sebastian Sager, Moritz Diehl
# SPDX-License-Identifier: GPL-3.0-or-later

"""An FNLP solver searching for the closest feasible point."""

import casadi as ca
import numpy as np
from camino.solvers import (
    SolverClass,
    Stats,
    MinlpProblem,
    MinlpData,
    regularize_options,
)
from camino.settings import GlobalSettings, Settings
from camino.utils import colored
from camino.utils.conversion import to_0d
import logging

logger = logging.getLogger(__name__)


class FindClosestNlpSolver(SolverClass):
    """Find closest feasible."""

    def __init__(self, problem: MinlpProblem, stats: Stats, s: Settings):
        """Create NLP problem."""
        super(FindClosestNlpSolver, self).__init__(problem, stats, s)
        options = regularize_options(s.IPOPT_SETTINGS, {"jit": s.WITH_JIT}, s)
        self.idx_x_integer = problem.idx_x_integer
        x_hat = GlobalSettings.CASADI_VAR.sym("x_hat", len(self.idx_x_integer))
        x_best = GlobalSettings.CASADI_VAR.sym("x_best", len(self.idx_x_integer))
        if problem.idx_g_dwelltime is not None:
            new_g_constraint = problem.g[problem.idx_g_without_dwelltime]
        else:
            new_g_constraint = problem.g
        self.idx_g_without_dwelltime = problem.idx_g_without_dwelltime

        f = ca.norm_2(problem.x[self.idx_x_integer] - x_hat) ** 2
        self.solver = ca.nlpsol(
            "nlpsol",
            "ipopt",
            {
                "f": f,
                "g": ca.vertcat(
                    new_g_constraint,
                    ca.dot(
                        problem.x[self.idx_x_integer] - x_best,
                        problem.x[self.idx_x_integer] - x_best,
                    ),
                ),
                "x": problem.x,
                "p": ca.vertcat(problem.p, x_hat, x_best),
            },
            options,
        )

    def solve(self, nlpdata: MinlpData) -> MinlpData:
        """Solve NLP."""
        success_out = []
        sols_out = []
        has_best = len(nlpdata.best_solutions) >= 1
        if has_best:
            x_best = nlpdata.best_solutions[-1]["x"][self.idx_x_integer]
        for success_prev, sol in zip(nlpdata.solved_all, nlpdata.solutions_all):
            if success_prev:
                success_out.append(success_prev)
                sols_out.append(sol)
            else:
                lbx = nlpdata.lbx
                ubx = nlpdata.ubx
                x_bin_var = to_0d(sol["x"][self.idx_x_integer])
                if not has_best:
                    x_best = x_bin_var
                    distance = 1e16
                else:
                    distance = ca.dot(x_best - x_bin_var, x_best - x_bin_var)

                sol_new = self.solver(
                    x0=nlpdata.x0,
                    lbx=lbx,
                    ubx=ubx,
                    lbg=ca.vertcat(
                        nlpdata.lbg[self.idx_g_without_dwelltime].flatten(), 0
                    ),
                    ubg=ca.vertcat(
                        nlpdata.ubg[self.idx_g_without_dwelltime].flatten(), distance
                    ),
                    p=ca.vertcat(nlpdata.p, x_bin_var, x_best),
                )
                sol_new["x_infeasible"] = sol["x"]
                success, _ = self.collect_stats("FC-NLP", sol=sol_new)
                if not success:
                    logger.warning(colored("FC-NLP not solved", "yellow"))

                success_out.append(False)
                sols_out.append(sol_new)

        nlpdata.prev_solutions = sols_out
        nlpdata.solved_all = success_out
        return nlpdata
