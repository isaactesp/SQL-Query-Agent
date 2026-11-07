from sql_query_agent.data.generate import generate


def test_generate_is_deterministic():
    assert generate(seed=1)["orders"] == generate(seed=1)["orders"]


def test_generate_writes_csvs(tmp_path):
    generate(tmp_path)
    for name in ("orders_raw.csv", "customers_raw.csv", "products_raw.csv"):
        assert (tmp_path / name).exists()


def test_orders_contain_injected_quality_issues():
    orders = generate()["orders"]
    ids = [o["order_id"] for o in orders]
    assert len(ids) > len(set(ids)), "expected duplicate order_ids"
    assert any(o["customer_id"] == "" for o in orders), "expected null customer_ids"
    assert any(o["quantity"] <= 0 for o in orders), "expected invalid quantities"
    assert any("/" in o["order_date"] for o in orders), "expected US-format dates"
