# About `hpg-lib`

This is a Python/SageMath implementation of hourglass plabic graphs (HPG's). Key functionality includes a programmatic representation of the underlying graphical objects suitable for computing trip permutations, generating non-elliptic SL(3) webs, performing square and some other moves, exploring move classes, computing dual diskoids, computing separation labels and SL(4) pockets, and more. See [[GPPSS25]](https://arxiv.org/abs/2306.12501) for mathematical details.

# Installation and basic usage

This repository contains only the Python backend. Follow these instructions to install it in your system Sage. Afterwards, if you wish to use the UI graph editor and analyzer, follow the installation instructions at the companion project [hpg-studio](https://github.com/Diagrammatics-Web/hpg-studio).

You must have a working installation of [SageMath](https://doc.sagemath.org/html/en/installation/index.html). To install the current development version of `hpg-lib` in the system `sage`, run the following, either in a terminal or in Sage itself:

    sage -pip install git+https://github.com/Diagrammatics-Web/hpg-lib/
  
From inside Sage, the library may be used as in the following example:

    sage: import hpg_lib
    sage: G = hpg_lib.Examples.get_example("example_ASM")
    sage: G.get_trip_perm(1)  # computes the first trip permutation
    [2, 5, 4, 7, 6, 1, 8, 3]
    sage: G.plot()            # plots this HPG with the default viewer
