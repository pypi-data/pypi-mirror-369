import os
import logging
import shlex
from dv_flow.mgr import TaskDataResult

_log = logging.getLogger("Exe")

async def Exe(runner, input):
    """
    Builds an executable from a set of FileSet objects.
    """
    cc = getattr(input.params, "cc", "gcc")
    cxx = getattr(input.params, "cxx", "g++")
    exename = getattr(input.params, "libname")  # flow.dv uses 'libname'
    rundir = input.rundir

    src_files_c = []
    src_files_cpp = []
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

        for inc in fs_incdirs:
            incdirs.add(inc)
        for define in fs_defines:
            defines.add(define)

        for f in files:
            if not os.path.isabs(basedir):
                abs_basedir = os.path.abspath(os.path.join(rundir, "..", basedir))
            else:
                abs_basedir = basedir
            full_path = os.path.abspath(os.path.join(abs_basedir, f))
            if filetype == "cSource":
                src_files_c.append(full_path)
            elif filetype == "cppSource":
                src_files_cpp.append(full_path)
                has_cpp = True
            elif filetype == "objFile":
                obj_files.append(full_path)

    # Compile C and C++ sources to object files
    all_obj_files = list(obj_files)
    compile_cmds = []
    for src in src_files_c:
        obj = os.path.join(rundir, os.path.basename(src) + ".o")
        cmd = [cc, "-c", "-o", obj]
        for inc in sorted(incdirs):
            cmd.append(f"-I{inc}")
        for define in sorted(defines):
            cmd.append(f"-D{define}")
        cmd.append(src)
        compile_cmds.append((cmd, obj))
        all_obj_files.append(obj)
    for src in src_files_cpp:
        obj = os.path.join(rundir, os.path.basename(src) + ".o")
        cmd = [cxx, "-c", "-o", obj]
        for inc in sorted(incdirs):
            cmd.append(f"-I{inc}")
        for define in sorted(defines):
            cmd.append(f"-D{define}")
        cmd.append(src)
        compile_cmds.append((cmd, obj))
        all_obj_files.append(obj)

    # Ensure rundir exists
    os.makedirs(rundir, exist_ok=True)

    # Run compile commands
    for cmd, obj in compile_cmds:
        _log.debug(f"Compiling: {' '.join(shlex.quote(x) for x in cmd)}")
        try:
            await runner.exec(cmd, cwd=rundir)
        except Exception as e:
            _log.error(f"Failed to compile {obj}: {e}")
            raise

    # Link all object files into the executable
    compiler = cxx if has_cpp else cc
    out_exe = os.path.abspath(os.path.join(rundir, "..", exename))
    link_cmd = [compiler, "-o", out_exe]
    link_cmd.extend(all_obj_files)
    _log.debug(f"Linking executable: {' '.join(shlex.quote(x) for x in link_cmd)}")

    try:
        await runner.exec(link_cmd, cwd=rundir)
        changed = True
    except Exception as e:
        _log.error(f"Failed to link executable: {e}")
        raise

    from dv_flow.mgr.fileset import FileSet

    output_fileset = FileSet(
        filetype="exe",
        basedir=os.path.dirname(out_exe),
        files=[exename],
        src=exename
    )

    return TaskDataResult(
        changed=changed,
        output=[output_fileset]
    )
