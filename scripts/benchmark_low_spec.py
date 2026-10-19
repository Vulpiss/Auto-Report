"""Windows constrained-resource benchmark of the shipped ZIP, using only stdlib.
No changes to source/release files. No machine-wide resource/settings changes.
"""
import ctypes as C
from ctypes import wintypes as W
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time
import zipfile

ROOT = Path(__file__).resolve().parents[1]
K = C.WinDLL("kernel32", use_last_error=True)
P = C.WinDLL("psapi", use_last_error=True)
SIZE = C.c_size_t
ULONG_PTR = C.c_size_t

class STARTUPINFO(C.Structure):
    _fields_ = [("cb", W.DWORD), ("lpReserved", W.LPWSTR), ("lpDesktop", W.LPWSTR),
                ("lpTitle", W.LPWSTR), ("dwX", W.DWORD), ("dwY", W.DWORD),
                ("dwXSize", W.DWORD), ("dwYSize", W.DWORD), ("dwXCountChars", W.DWORD),
                ("dwYCountChars", W.DWORD), ("dwFillAttribute", W.DWORD), ("dwFlags", W.DWORD),
                ("wShowWindow", W.WORD), ("cbReserved2", W.WORD),
                ("lpReserved2", C.POINTER(C.c_byte)), ("hStdInput", W.HANDLE),
                ("hStdOutput", W.HANDLE), ("hStdError", W.HANDLE)]

class PROCESS_INFORMATION(C.Structure):
    _fields_ = [("hProcess", W.HANDLE), ("hThread", W.HANDLE), ("dwProcessId", W.DWORD), ("dwThreadId", W.DWORD)]

class BASIC_LIMIT(C.Structure):
    _fields_ = [("PerProcessUserTimeLimit", C.c_int64), ("PerJobUserTimeLimit", C.c_int64),
                ("LimitFlags", W.DWORD), ("MinimumWorkingSetSize", SIZE), ("MaximumWorkingSetSize", SIZE),
                ("ActiveProcessLimit", W.DWORD), ("Affinity", ULONG_PTR),
                ("PriorityClass", W.DWORD), ("SchedulingClass", W.DWORD)]

class IO_COUNTERS(C.Structure):
    _fields_ = [(n, C.c_uint64) for n in ("ReadOperationCount", "WriteOperationCount", "OtherOperationCount",
                                       "ReadTransferCount", "WriteTransferCount", "OtherTransferCount")]

class EXTENDED_LIMIT(C.Structure):
    _fields_ = [("BasicLimitInformation", BASIC_LIMIT), ("IoInfo", IO_COUNTERS),
                ("ProcessMemoryLimit", SIZE), ("JobMemoryLimit", SIZE),
                ("PeakProcessMemoryUsed", SIZE), ("PeakJobMemoryUsed", SIZE)]

class MEMORY(C.Structure):
    _fields_ = [("cb", W.DWORD), ("PageFaultCount", W.DWORD)] + [
        (n, SIZE) for n in ("PeakWorkingSetSize", "WorkingSetSize", "QuotaPeakPagedPoolUsage",
                           "QuotaPagedPoolUsage", "QuotaPeakNonPagedPoolUsage", "QuotaNonPagedPoolUsage",
                           "PagefileUsage", "PeakPagefileUsage", "PrivateUsage")]

def api(dll, name, args, result):
    fn = getattr(dll, name)
    fn.argtypes, fn.restype = args, result
    return fn

create_job = api(K, "CreateJobObjectW", [C.c_void_p, W.LPCWSTR], W.HANDLE)
set_job = api(K, "SetInformationJobObject", [W.HANDLE, C.c_int, C.c_void_p, W.DWORD], W.BOOL)
query_job = api(K, "QueryInformationJobObject", [W.HANDLE, C.c_int, C.c_void_p, W.DWORD, C.c_void_p], W.BOOL)
create_process = api(K, "CreateProcessW", [W.LPCWSTR, W.LPWSTR, C.c_void_p, C.c_void_p, W.BOOL, W.DWORD,
                                          C.c_void_p, W.LPCWSTR, C.POINTER(STARTUPINFO), C.POINTER(PROCESS_INFORMATION)], W.BOOL)
assign_job = api(K, "AssignProcessToJobObject", [W.HANDLE, W.HANDLE], W.BOOL)
resume = api(K, "ResumeThread", [W.HANDLE], W.DWORD)
wait = api(K, "WaitForSingleObject", [W.HANDLE, W.DWORD], W.DWORD)
exit_code = api(K, "GetExitCodeProcess", [W.HANDLE, C.POINTER(W.DWORD)], W.BOOL)
close = api(K, "CloseHandle", [W.HANDLE], W.BOOL)
terminate = api(K, "TerminateProcess", [W.HANDLE, W.UINT], W.BOOL)
memory_info = api(P, "GetProcessMemoryInfo", [W.HANDLE, C.POINTER(MEMORY), W.DWORD], W.BOOL)
get_times = api(K, "GetProcessTimes", [W.HANDLE] + [C.POINTER(W.FILETIME)] * 4, W.BOOL)

def require(ok):
    if not ok:
        raise C.WinError(C.get_last_error())

def run(exe, output, memory_mb, cpu_mask=1):
    job = create_job(None, None)
    require(job)
    pi = PROCESS_INFORMATION()
    try:
        limits = EXTENDED_LIMIT()
        limits.BasicLimitInformation.LimitFlags = 0x2000 | 0x100 | 0x10  # kill on close, private commit cap, affinity
        limits.BasicLimitInformation.Affinity = cpu_mask
        limits.ProcessMemoryLimit = memory_mb * 1024**2
        require(set_job(job, 9, C.byref(limits), C.sizeof(limits)))
        check = EXTENDED_LIMIT()
        require(query_job(job, 9, C.byref(check), C.sizeof(check), None))
        assert check.ProcessMemoryLimit == memory_mb * 1024**2
        assert check.BasicLimitInformation.Affinity == cpu_mask
        env = {key: value for key, value in os.environ.items()
               if not key.upper().startswith(("PYTHON", "CONDA", "VIRTUAL_ENV"))}
        env["PATH"] = str(Path(os.environ["SystemRoot"]) / "System32")
        env["AUTOREPORT_HOME"] = str(output / "home")
        env["MPLCONFIGDIR"] = str(output / "mpl")
        env["OPENBLAS_NUM_THREADS"] = "1"
        env["OMP_NUM_THREADS"] = "1"
        output.mkdir(parents=True)
        environment = C.create_unicode_buffer("\0".join(f"{k}={v}" for k, v in sorted(env.items(), key=lambda p: p[0].upper())) + "\0\0")
        command = C.create_unicode_buffer(subprocess.list2cmdline([str(exe), "--smoke-test", str(output)]))
        si = STARTUPINFO()
        si.cb = C.sizeof(si)
        started = time.perf_counter()
        require(create_process(str(exe), command, None, None, False, 0x4 | 0x400 | 0x08000000,
                               environment, str(output), C.byref(si), C.byref(pi)))
        require(assign_job(job, pi.hProcess))
        if resume(pi.hThread) == 0xFFFFFFFF:
            require(False)
        peak_ws, peak_private = 0, 0
        timed_out = False
        while True:
            state = wait(pi.hProcess, 50)
            if state == 0xFFFFFFFF:
                require(False)
            mem = MEMORY()
            mem.cb = C.sizeof(mem)
            if memory_info(pi.hProcess, C.byref(mem), C.sizeof(mem)):
                peak_ws = max(peak_ws, mem.PeakWorkingSetSize)
                peak_private = max(peak_private, mem.PeakPagefileUsage)
            if state == 0:
                break
            if time.perf_counter() - started > 90:
                timed_out = True
                terminate(pi.hProcess, 124)
                wait(pi.hProcess, 5000)
                break
        elapsed = time.perf_counter() - started
        code = W.DWORD()
        require(exit_code(pi.hProcess, C.byref(code)))
        require(query_job(job, 9, C.byref(check), C.sizeof(check), None))
        cpu_seconds = None
        times = [W.FILETIME() for _ in range(4)]
        if get_times(pi.hProcess, *(C.byref(t) for t in times)):
            cpu_seconds = sum((t.dwHighDateTime << 32) + t.dwLowDateTime for t in times[2:]) / 10**7
        return {"exit_code": code.value, "timeout": timed_out, "wall_seconds": round(elapsed, 3),
                "cpu_seconds": round(cpu_seconds, 3) if cpu_seconds is not None else None,
                "peak_working_set_mb": round(peak_ws / 1024**2, 2),
                "peak_private_commit_mb": round(max(peak_private, check.PeakProcessMemoryUsed) / 1024**2, 2),
                "memory_limit_mb": memory_mb, "logical_processors": 1,
                "path_contains_python": False}
    finally:
        if pi.hProcess:
            if wait(pi.hProcess, 0) == 258:
                terminate(pi.hProcess, 125)
                wait(pi.hProcess, 5000)
            close(pi.hProcess)
        if pi.hThread:
            close(pi.hThread)
        close(job)

def main(stress=False):
    archive = ROOT / "release/AutoReport-v0.2.0-Windows.zip"
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    work = ROOT / "build" / ("low-spec-" + stamp)
    unpacked = work / "unpacked"
    unpacked.mkdir(parents=True)
    with zipfile.ZipFile(archive) as z:
        for name in z.namelist():
            if not (unpacked / name).resolve().is_relative_to(unpacked.resolve()):
                raise ValueError("Archive path outside test directory")
        z.extractall(unpacked)
    exe = next(unpacked.rglob("AutoReport.exe"))
    data = exe.parent / "_internal/sample_data/pilot_demo.csv"
    assert data.is_file()
    report = {"created_utc": stamp, "archive_sha256": hashlib.sha256(archive.read_bytes()).hexdigest(),
              "exe_sha256": hashlib.sha256(exe.read_bytes()).hexdigest(),
              "environment": "Extracted ZIP, isolated cwd, no Python in child PATH; host OS is not a clean VM.",
              "acceptance": {"exit_code": 0, "correct_total_minor": True, "max_wall_seconds": 30,
                             "required_memory_limit_mb": 512},
              "runs": []}
    cases = [(100000, 512)] if stress else [(1000, 512), (10000, 512), (100000, 512), (100000, 256)]
    for size, cap in cases:
        # Only synthetic data in the extracted COPY changes. Expected sum = N cents.
        if stress:
            csv_text = "date,value,category\n" + "".join(f"2026-09-13,0.01,Kategoria-{i:06d}-" + "x" * 150 + "\n" for i in range(size))
        else:
            csv_text = "date,value,category\n" + "2026-09-13,0.01,Papier\n" * size
        data.write_text(csv_text, encoding="utf-8")
        for repeat in range(1, 4):
            output = work / f"rows-{size}-cap-{cap}-run-{repeat}"
            result = run(exe, output, cap)
            result.update({"rows": size, "repeat": repeat, "correct": False, "dataset": "long unique categories" if stress else "simple repeated rows", "csv_bytes": data.stat().st_size})
            marker = output / "smoke-result.json"
            if result["exit_code"] == 0 and marker.exists():
                pdf = Path(json.loads(marker.read_text())["output"])
                summary = json.loads((pdf.parent / "summary.json").read_text(encoding="utf-8"))
                result["correct"] = (summary["kpis"]["total_minor"] == size and summary["kpis"]["rows_cnt"] == size
                                     and pdf.read_bytes().startswith(b"%PDF"))
            result["passed"] = result["exit_code"] == 0 and result["correct"] and result["wall_seconds"] <= 30
            report["runs"].append(result)
            print(json.dumps(result), flush=True)
            (work / "results.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    report["required_passed"] = all(r["passed"] for r in report["runs"] if r["memory_limit_mb"] == 512)
    (work / "results.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    (ROOT / "build" / "low-spec-latest.txt").write_text(str(work / "results.json"), encoding="utf-8")
    print("RESULTS: " + str(work / "results.json"), flush=True)
    if not report["required_passed"]:
        raise SystemExit(1)

if __name__ == "__main__":
    main()
