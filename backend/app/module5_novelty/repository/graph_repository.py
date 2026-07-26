from sqlalchemy.orm import Session
from sqlalchemy import text

class GraphRepository:
    @staticmethod
    def get_nodes(db: Session) -> list[dict]:
        res = db.execute(text("SELECT id, node_type, name FROM graph_nodes")).fetchall()
        return [{"id": r[0], "node_type": r[1], "name": r[2]} for r in res]

    @staticmethod
    def get_edges(db: Session) -> list[dict]:
        res = db.execute(text("SELECT id, from_node, to_node, relationship, confidence FROM graph_edges")).fetchall()
        return [
            {
                "id": r[0],
                "from_node": r[1],
                "to_node": r[2],
                "relationship": r[3],
                "confidence": float(r[4] or 1.0)
            }
            for r in res
        ]
