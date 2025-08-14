"""
moducomp: Metabolic module completeness of genomes and metabolic complementarity in microbiomes

This module provides a comprehensive bioinformatics pipeline for analyzing metabolic
module completeness in microbial genomes and identifying complementarity patterns
in microbial communities.

Key Features:
- Protein annotation using eggNOG-mapper to obtain KO (KEGG Orthology) terms
- Mapping of KO terms to KEGG metabolic modules using KPCT
- Parallel processing support for improved performance
- Module completeness analysis for individual genomes
- Complementarity analysis for N-member genome combinations
- Protein-level tracking for module completion

Author: Juan C. Villada - US DOE Joint Genome Institute - Lawrence Berkeley National Lab
License: See LICENSE.txt
Version: See pyproject.toml for current version
"""

__version__ = "0.6.0"
__author__ = "Juan C. Villada"
__email__ = "jvillada@lbl.gov"

from .cli import app

__all__ = ["app"]
