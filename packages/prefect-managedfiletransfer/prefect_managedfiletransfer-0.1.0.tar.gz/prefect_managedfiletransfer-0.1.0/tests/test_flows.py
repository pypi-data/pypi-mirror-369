from prefect_managedfiletransfer.flows import hello_and_goodbye


def test_hello_and_goodbye_flow(prefect_db):
    result = hello_and_goodbye()
    assert result == "Done"
