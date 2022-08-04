from flask import request
from requests import get
from hn_transform.app import app
from ignorance_transform.node import Node
from ignorance_transform.transform import Transform

USER_BASE_URL = "https://hacker-news.firebaseio.com/v0/user/{}.json"


@app.route("/user/items", methods=["POST"])
def get_user():
    transform = Transform(request.json)
    for node in transform.nodes:
        if "userid" not in node.data:
            continue
        resp = get(USER_BASE_URL.format(node.data["userid"]))
        if not resp.ok:
            continue
        resp_json = resp.json()
        node.label = resp_json["id"]
        node.update_data({
            "created": resp_json.get("created", "N/A"),
            "karma": resp_json.get("karma", "N/A"),
            "about": resp_json.get("about", "N/A"),
            "type": "hn.user",
            "color": "#54c4e3",
        })

        for item in resp_json["submitted"]:
            item_node = Node()
            item_node.label = str(item)
            item_node.update_data({
                "type": "item",
                "itemid": str(item),
            })
            edge = node.link_to(item_node, "posted")
            transform.add_node(item_node)
            transform.add_edge(edge)

    return transform.to_dict()
