from bmailer.templates import render_template


def test_render_template() -> None:
    name = "Duy Tan"
    order_id = 123
    template = "Hello {name},\nYour order #{order_id} has been shipped."
    rendered = render_template(template, name=name, order_id=order_id)
    expected = f"Hello {name},\nYour order #{order_id} has been shipped."
    assert rendered == expected
