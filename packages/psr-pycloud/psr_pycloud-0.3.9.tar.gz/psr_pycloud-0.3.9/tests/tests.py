# PSR Cloud. Copyright (C) PSR, Inc - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

import os
import sys

from dotenv import load_dotenv

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from psr.cloud import Case, Client, ExecutionStatus

CASES_PATH = os.path.abspath(".\\tests\\cases")

TIMEOUT_SECONDS = 60 * 60 * 24  # 24 hours

DEFAULT_NUMBER_OF_PROCESSES = 64


def create_client():
    if os.path.exists(".env"):
        load_dotenv()
    if "PSRCLOUD_TEST_CLUSTER" in os.environ:
        cluster = os.environ["PSRCLOUD_TEST_CLUSTER"]
    else:
        cluster = "Staging"
    client = Client(cluster=cluster, import_desktop=False)
    return client


def test_download_results():
    client = create_client()

    download_path = os.path.join(CASES_PATH, "results")
    client._clean_folder(download_path)

    case = Case(
        name="test_download_results",
        data_path=os.path.join(CASES_PATH, "example"),
        program="SDDP",
        program_version="17.3.7",
        execution_type="Default",
        memory_per_process_ratio="2:1",
        price_optimized=True,
        number_of_processes=DEFAULT_NUMBER_OF_PROCESSES,
        repository_duration=1,
    )
    case_id = client.run_case(case)
    assert client._check_until_status(
        case_id, ExecutionStatus.SUCCESS, timeout=TIMEOUT_SECONDS
    )
    client.download_results(case_id, download_path)
    assert os.path.exists(os.path.join(download_path, "download.ok"))
    client._clean_folder(download_path)


def test_cancel_case():
    client = create_client()
    case = Case(
        name="test_cancel_case",
        data_path=os.path.join(CASES_PATH, "sddp_quick"),
        program="SDDP",
        program_version="17.3.7",
        execution_type="Default",
        memory_per_process_ratio="2:1",
        price_optimized=True,
        number_of_processes=DEFAULT_NUMBER_OF_PROCESSES,
        repository_duration=1,
    )
    case_id = client.run_case(case)
    assert client._check_until_status(
        case_id, ExecutionStatus.RUNNING, timeout=TIMEOUT_SECONDS
    )
    assert client.cancel_case(case_id)


def test_get_soap_objects():
    client = create_client()
    programs = client.get_programs()
    assert len(programs) > 0
    for program in programs:
        program_versions = client.get_program_versions(program)
        assert len(program_versions) > 0
        for version in program_versions.values():
            execution_types = client.get_execution_types(program, version)
            assert len(execution_types) >= 0
    assert len(client.get_memory_per_process_ratios()) > 0
    assert len(client.get_repository_durations()) > 0
    assert len(client.get_budgets()) >= 0


# def test_get_case():
#    client = create_client()
#    cases = client.get_all_cases_since(365)
#    assert len(cases) > 0
#    assert isinstance(client.get_case(cases[0].id), Case)


def test_psrio():
    client = create_client()
    sddp_case = Case(
        name="test_psrio_sddp",
        data_path=os.path.join(CASES_PATH, "example"),
        program="SDDP",
        program_version="17.3.7",
        execution_type="Default",
        memory_per_process_ratio="2:1",
        price_optimized=True,
        number_of_processes=DEFAULT_NUMBER_OF_PROCESSES,
        repository_duration=1,
    )
    sddp_case_id = client.run_case(sddp_case)
    assert client._check_until_status(
        sddp_case_id, ExecutionStatus.SUCCESS, timeout=TIMEOUT_SECONDS
    )

    psrio_case = Case(
        name="test_psrio",
        data_path=os.path.join(CASES_PATH, "psrio"),
        program="PSRIO",
        execution_type="SDDP",
        program_version="1.2.0",
        memory_per_process_ratio="2:1",
        price_optimized=True,
        number_of_processes=1,
        repository_duration=1,
        parent_case_id=sddp_case_id,
    )
    psrio_case_id = client.run_case(psrio_case)
    assert client._check_until_status(
        psrio_case_id, ExecutionStatus.SUCCESS, timeout=TIMEOUT_SECONDS
    )


def test_sddp_policy_simulation():
    client = create_client()
    policy_case = Case(
        name="test_sddp_policy",
        data_path=os.path.join(CASES_PATH, "sddp_policy"),
        program="SDDP",
        program_version="17.3.7",
        execution_type="Default",
        memory_per_process_ratio="2:1",
        price_optimized=True,
        number_of_processes=DEFAULT_NUMBER_OF_PROCESSES,
        repository_duration=1,
    )
    policy_case_id = client.run_case(policy_case)
    # There is no wait until status here beacuse both cases must be queued at the same time
    # and it is up to the server to wait until the policy case is finished to start the simulation case

    simulation_case = Case(
        name="test_sddp_simulation",
        data_path=os.path.join(CASES_PATH, "sddp_simulation"),
        program="SDDP",
        program_version="17.3.7",
        execution_type="Default",
        memory_per_process_ratio="2:1",
        price_optimized=True,
        number_of_processes=DEFAULT_NUMBER_OF_PROCESSES,
        repository_duration=1,
        parent_case_id=policy_case_id,
    )
    sim_case_id = client.run_case(simulation_case)
    assert client._check_until_status(
        sim_case_id, ExecutionStatus.SUCCESS, timeout=TIMEOUT_SECONDS
    )


def test_graf():
    client = create_client()

    graf_files_path = os.path.abspath(os.path.join(CASES_PATH, "graf"))
    client._clean_folder(graf_files_path)

    sddp_case = Case(
        name="test_graf_sddp",
        data_path=os.path.join(CASES_PATH, "sddp_quick"),
        program="SDDP",
        program_version="17.3.7",
        execution_type="Default",
        memory_per_process_ratio="2:1",
        price_optimized=True,
        number_of_processes=DEFAULT_NUMBER_OF_PROCESSES,
        repository_duration=1,
    )
    sddp_case_id = client.run_case(sddp_case)
    assert client._check_until_status(
        sddp_case_id, ExecutionStatus.SUCCESS, timeout=TIMEOUT_SECONDS
    )

    client._pre_process_graph(graf_files_path, sddp_case_id)
    assert os.path.exists(os.path.join(graf_files_path, "indice.grf"))

    graf_name = "test_graf"
    with open(os.path.join(graf_files_path, "instruc.grf"), "w") as f:
        f.write(f"""INIGRAPH {graf_name}
HORIZON,-1
Etapa inicial           :    1
Ano inicial             : 2013
Etapa final             :   12
Ano final               : 2013
# bloques a graficar    :   -1
Suma bloques?           :    1
Suma etapas por ano?    :   -1
Titulo eje-x            :     
Titulo primario eje-y   :     
Titulo secundario eje-y :
# Series seleccionadas  :   -1
grafica series selecc.? :   -1
grafica promedio?       :    1
grafica desv. standard? :   -1
grafica cuantil sup?    :    0
grafica cuantil inf?    :    0
CHARTTYPE -1
CHARTNAME 1
Nombre variable   1     :Block length in pu
# de agentes a graficar :00001
nombre del agente       :Length
ENDGRAPH""")

    graf_case = Case(
        name="test_graf",
        data_path=graf_files_path,
        program="GRAF",
        execution_type="Old Compatibility",
        program_version="0",
        memory_per_process_ratio="2:1",
        price_optimized=True,
        number_of_processes=1,
        repository_duration=1,
        parent_case_id=sddp_case_id,
    )
    client.run_case(graf_case)
    assert os.path.exists(os.path.join(graf_files_path, f"GRAF-{graf_name}.csv"))
    assert os.path.exists(os.path.join(graf_files_path, "graf.ok"))
    client._clean_folder(graf_files_path)


def test_optgen():
    client = create_client()
    case = Case(
        name="test_optgen",
        data_path=os.path.join(CASES_PATH, "optgen"),
        program="OPTGEN",
        program_version="8.2.4",
        execution_type="SDDP 17.3.12",
        memory_per_process_ratio="2:1",
        price_optimized=True,
        number_of_processes=DEFAULT_NUMBER_OF_PROCESSES,
        repository_duration=1,
    )
    case_id = client.run_case(case)
    assert client._check_until_status(case_id, ExecutionStatus.SUCCESS)
