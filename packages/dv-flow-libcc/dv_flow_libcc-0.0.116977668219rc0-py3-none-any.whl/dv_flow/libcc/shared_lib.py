import os
import logging
import shlex
import subprocess
from dv_flow.mgr import TaskDataResult

_log = logging.getLogger("SharedLib")

async def SharedLib(runner, input):
    """
    Builds a shared library from a set of FileSet objects.
    """
    # Gather parameters
    cc = getattr(input.params, "cc", "gcc")
    cxx = getattr(input.params, "cxx", "g++")
    libname = getattr(input.params, "libname")
    rundir = input.rundir

    # Collect all files, include dirs, and defines
    src_files = []
    obj_files = []
    incdirs = set()
    defines = set()
    has_cpp = False

    for fs in input.inputs:
        filetype = getattr(fs, "filetype", None)
        basedir = getattr(fs, "basedir", "")
        files = getattr(fs, "files", [])
        fs_incdirs = getattr(fs, "incdirs", [])
        fs_defines = getattr(fs, "defines", [])

        # Collect include dirs and defines
        for inc in fs_incdirs:
            incdirs.add(inc)
        for define in fs_defines:
            defines.add(define)

        # Classify files
        for f in files:
            # If basedir is not absolute, make it relative to rundir's parent
            if not os.path.isabs(basedir):
                abs_basedir = os.path.abspath(os.path.join(rundir, "..", basedir))
            else:
                abs_basedir = basedir
            full_path = os.path.abspath(os.path.join(abs_basedir, f))
            if filetype == "cSource":
                src_files.append(full_path)
            elif filetype == "cppSource":
                src_files.append(full_path)
                has_cpp = True
            elif filetype == "objFile":
                obj_files.append(full_path)

    # Select compiler
    compiler = cxx if has_cpp else cc

    # Build output path
    # Place output in the parent of rundir (the test's tmp_path)
    out_lib = os.path.abspath(os.path.join(rundir, "..", f"lib{libname}.so"))

    # Build command
    cmd = [compiler, "-shared", "-o", out_lib]
    for inc in sorted(incdirs):
        cmd.append(f"-I{inc}")
    for define in sorted(defines):
        cmd.append(f"-D{define}")
    cmd.extend(src_files)
    cmd.extend(obj_files)

    _log.debug(f"Building shared library: {' '.join(shlex.quote(x) for x in cmd)}")

    # Ensure rundir exists
    os.makedirs(os.path.dirname(out_lib), exist_ok=True)

    # Run the command
    try:
        result = await runner.exec(cmd, cwd=rundir)
        changed = True
    except Exception as e:
        _log.error(f"Failed to build shared library: {e}")
        raise

    from dv_flow.mgr.fileset import FileSet

    output_fileset = FileSet(
        filetype="sharedLib",
        basedir=os.path.dirname(out_lib),
        files=[f"lib{libname}.so"],
        src=libname
    )

    return TaskDataResult(
        changed=changed,
        output=[output_fileset]
    )
