"""
Run InterProScan on multiple sequences
"""

import subprocess
from pathlib import Path

from latch.types import LatchFile, LatchDir, file_glob
from latch import small_task, workflow
from typing import List
from time import sleep
from Bio import SeqIO


@small_task
def read_fasta_files(
    fasta_dir: LatchDir
) -> List[LatchFile]:
    """
    Read all FASTA files in a directory.
    """
    def is_fasta(f):
        with open(f, "r") as handle:
            fasta = SeqIO.parse(handle, "fasta")
            return any(fasta)

    files = file_glob("*.fasta", fasta_dir)
    files.extend(file_glob("*.FASTA", fasta_dir))
    files.extend(file_glob("*.fa", fasta_dir))
    files.extend(file_glob("*.FA", fasta_dir))
    return [f for f in files if is_fasta(f)]


@small_task
def interproscan_task(
    email_addr: str, 
    fasta_files: List[LatchFile],
    output_dir: LatchDir,
    goterms: bool,
    pathways: bool,
) -> LatchFile:
    # sam_file = Path("covid_assembly.sam").resolve()
    return LatchFile(str(sam_file), "latch:///covid_assembly.sam")


@workflow
def interproscan(
    email_addr: str, 
    fasta_dir: LatchDir,
    output_dir: LatchDir,
    goterms: bool = False,
    pathways: bool = False,
) -> LatchFile:
    """Run InterProScan on multiple sequences

    InterProScan
    ----

    Run InterProScan on multiple protein sequences

    __metadata__:
        display_name: InterProScan
        author:
            name: Abdullah Al Nahid
            email:
            github:
        repository:
        license:
            id: MIT

    Args:

        email_addr:
          Your Email Address

          __metadata__:
            display_name: Email

        fasta_dir:
           Input Directory of Protein FASTA Sequences

          __metadata__:
            display_name: Input Directory (One Protein, One FASTA)

        output_dir:
           Output Directory of Results

          __metadata__:
            display_name: Output Directory

        goterms:
           GO Terms from InterProScan

          __metadata__:
            display_name: Include GO Terms

        pathways:
           Pathways from InterProScan

          __metadata__:
            display_name: Include Pathways

    """
    fasta_files = read_fasta_files(fasta_dir=fasta_dir)
    return interproscan_task(
        email_addr=email_addr, 
        fasta_files=fasta_files,
        output_dir=output_dir,
        goterms=goterms,
        pathways=pathways,
    )
