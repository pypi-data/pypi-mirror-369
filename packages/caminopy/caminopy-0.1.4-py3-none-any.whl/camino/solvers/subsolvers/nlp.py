# This file is part of CAMINO
# Copyright (C) 2024  Andrea Ghezzi, Wim Van Roy, Sebastian Sager, Moritz Diehl
# SPDX-License-Identifier: GPL-3.0-or-later

"""An NLP solver."""

import casadi as ca
import numpy as np
import logging
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

logger = logging.getLogger(__name__)


class NlpSolver(SolverClass):
    """
    Create NLP solver.

    This solver solves an NLP problem. This is either relaxed or
    the binaries are fixed.
    """

    def __init__(self, problem: MinlpProblem, stats: Stats, s: Settings):
        """Create NLP problem."""
        super(NlpSolver, self).__init__(problem, stats, s)
        options = regularize_options(
            s.IPOPT_SETTINGS,
            {
                "calc_multipliers": True,
                "ipopt.expect_infeasible_problem": "yes",
                "error_on_fail": False,
            },
            s,
        )

        self.idx_x_integer = problem.idx_x_integer
        # self.callback = DebugCallBack(
        #     'mycallback', problem.x.shape[0],
        #     problem.g.shape[0], problem.p.shape[0]
        # )
        # self.callback.add_to_solver_opts(options, 50)
        if problem.idx_g_dwelltime is not None:
            new_g_constraint = problem.g[problem.idx_g_without_dwelltime]
        else:
            new_g_constraint = problem.g
        self.idx_g_without_dwelltime = problem.idx_g_without_dwelltime
        self.g_fn = ca.Function("g", [problem.x, problem.p], [new_g_constraint])

        if problem.precompiled_nlp is not None:
            self.solver = ca.nlpsol("nlp", "ipopt", problem.precompiled_nlp, options)
        else:
            options.update(
                {
                    "jit": s.WITH_JIT,
                }
            )
            self.solver = ca.nlpsol(
                "nlpsol",
                "ipopt",
                {"f": problem.f, "g": new_g_constraint, "x": problem.x, "p": problem.p},
                options,
            )

    def solve(self, nlpdata: MinlpData, integers_relaxed=True) -> MinlpData:
        """Solve NLP."""
        success_out = []
        sols_out = []

        for sol in nlpdata.solutions_all:
            lbx = nlpdata.lbx
            ubx = nlpdata.ubx
            if not integers_relaxed:
                # Remove integer errors
                x_bin_var = np.round(to_0d(sol["x"][self.idx_x_integer]))
                lbx[self.idx_x_integer] = x_bin_var
                ubx[self.idx_x_integer] = x_bin_var

            sol_new = self.solver(
                p=nlpdata.p,
                x0=nlpdata.x0,
                lbx=lbx,
                ubx=ubx,
                lbg=nlpdata.lbg[self.idx_g_without_dwelltime].flatten(),
                ubg=nlpdata.ubg[self.idx_g_without_dwelltime].flatten(),
            )

            success, stats = self.collect_stats("NLP", sol=sol_new)
            if not success:
                return_status_ok = stats["return_status"] in [
                    "Search_Direction_Becomes_Too_Small",
                    "Maximum_Iterations_Exceeded",
                    "Maximum_CpuTime_Exceeded",
                    "Maximum_WallTime_Exceeded",
                    "Solved_To_Acceptable_Level",
                    "Feasible_Point_Found",
                    "Not_Enough_Degrees_Of_Freedom",
                    "Insufficient_Memory",
                ]
                if return_status_ok:
                    gk = self.g_fn(sol_new["x"], nlpdata.p).full()
                    if np.all(gk <= nlpdata.ubg) and np.all(gk >= nlpdata.lbg):
                        success = True
                    # if np.all(gk <= nlpdata.ubg + self.settings.CONSTRAINT_TOL) and \
                    #         np.all(gk >= nlpdata.lbg - self.settings.CONSTRAINT_TOL):
                    #     success = True
            if not success:
                logger.warning(colored("NLP not solved.", "yellow"))

            success_out.append(success)
            sols_out.append(sol_new)

        nlpdata.prev_solutions = sols_out
        nlpdata.solved_all = success_out

        return nlpdata
