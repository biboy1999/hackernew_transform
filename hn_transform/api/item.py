from flask import request
from requests import get
from hn_transform.app import app
from ignorance_transform.node import Node
from ignorance_transform.transform import Transform

BASE_URL = "https://hacker-news.firebaseio.com/v0/item/{}.json"


@app.route("/item", methods=["POST"])
def get_comment():
    transform = Transform(request.json)
    for node in transform.nodes:
        if "itemid" not in node.data:
            continue
        resp = get(BASE_URL.format(node.data["itemid"]))
        if not resp.ok:
            continue
        resp_json = resp.json()

        # different type
        if "deleted" in resp_json:
            node.label = "deleted"
            node.update_data({
                "color": "#FF0000",
                "time": resp_json["time"],
                "type": "hn.deleted",
            })
        elif resp_json["type"] == "story":
            node.label = resp_json["title"][:30]
            node.update_data({
                "color": "#fa7b61",
                "descendants": resp_json["descendants"],
                "userid": resp_json["by"],
                "score": resp_json["score"],
                "time": resp_json["time"],
                "url": resp_json["url"],
                "type": "hn.story",
            })
            for item in resp_json.get("kids", []):
                item_node = Node()
                item_node.label = str(item)
                item_node.update_data({
                    "type": "item",
                    "itemid": str(item),
                })
                edge = node.link_to(item_node)
                transform.add_node(item_node)
                transform.add_edge(edge)
            pass
        elif resp_json["type"] == "comment":
            node.label = resp_json["text"][:30]
            node.update_data({
                "color": "#effa73",
                "userid": resp_json["by"],
                "time": resp_json["time"],
                "parent": resp_json["parent"],
                "text": resp_json["text"],
                "type": "hn.comment",
            })

            for item in resp_json.get("kids", []):
                item_node = Node()
                item_node.label = str(item)
                item_node.update_data({
                    "type": "item",
                    "itemid": str(item),
                })
                edge = node.link_to(item_node)
                transform.add_node(item_node)
                transform.add_edge(edge)
        elif resp_json["type"] == "job":
            node.label = resp_json["title"]
            node.update_data({
                "color": "#7cfa73",
                "userid": resp_json["by"],
                "score": resp_json["score"],
                "text": resp_json["text"],
                "time": resp_json["time"],
                "title": resp_json["title"],
                "url": resp_json["url"],
                "type": "hn.job",
            })

            pass
        elif resp_json["type"] == "poll":
            node.label = resp_json["title"]
            node.update_data({
                "color": "#fa73fa",
                "userid": resp_json["by"],
                "score": resp_json["score"],
                "text": resp_json["text"],
                "time": resp_json["time"],
                "title": resp_json["title"],
                "type": "hn.poll",
            })

            for item in resp_json.get("kids", []):
                item_node = Node()
                item_node.label = str(item)
                item_node.update_data({
                    "type": "item",
                    "itemid": str(item),
                })
                edge = node.link_to(item_node)
                transform.add_node(item_node)
                transform.add_edge(edge)

            for item in resp_json.get("parts", []):
                item_node = Node()
                item_node.label = str(item)
                item_node.update_data({
                    "type": "hn.poll.part",
                    "itemid": str(item),
                })
                edge = node.link_to(item_node, "poll part")
                transform.add_node(item_node)
                transform.add_edge(edge)

            pass
        elif resp_json["type"] == "pollopt":
            node.label = resp_json["text"]
            node.update_data({
                "color": "#f0b4e3",
                "userid": resp_json["by"],
                "score": resp_json["score"],
                "text": resp_json["text"],
                "time": resp_json["time"],
                "poll": resp_json["poll"],
                "type": "hn.pollopt",
            })
    return transform.to_dict()
