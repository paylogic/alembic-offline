"""Tests for the migration graph."""

from alembic.config import Config

from alembic_offline import generate_migration_graph


def test_migration_graph_simple():
    """Test migration graph for simple case"""
    config = Config()
    config.set_main_option("script_location", "tests.graph:migrations")
    config.set_main_option("phases", "before-deploy after-deploy final")
    config.set_main_option("default-phase", "after-deploy")
    config.set_main_option("sqlalchemy.url", "sqlite:///")
    config.set_main_option("script-attributes", "some_attribute")

    dotfile = generate_migration_graph(config)
    expected = (
        u"digraph revisions {\n"
        "\t\"1\" [label=\"1\\n- some_attribute: some-base-value\"];\n"
        "\t\"simple\" [label=\"simple\\n- some_attribute: some-value\"];\n"
        "\n"
        "\t\"simple\" -> \"1\";\n"
        "}"
    )
    assert dotfile == expected


def test_migration_graph_custom_label():
    """Test migration graph for simple case with custom label"""
    config = Config()
    config.set_main_option("script_location", "tests.graph:migrations")
    config.set_main_option("phases", "before-deploy after-deploy final")
    config.set_main_option("default-phase", "after-deploy")
    config.set_main_option("sqlalchemy.url", "sqlite:///")
    config.set_main_option("script-attributes", "some_attribute")

    dotfile = generate_migration_graph(config, lambda data: data['revision'])
    expected = (
        u"digraph revisions {\n"
        "\t\"1\" [label=\"1\"];\n"
        "\t\"simple\" [label=\"simple\"];\n"
        "\n"
        "\t\"simple\" -> \"1\";\n"
        "}"
    )
    assert dotfile == expected
