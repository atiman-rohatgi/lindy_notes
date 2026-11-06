from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from database import get_connection
from auth import get_current_user

router = APIRouter(prefix="/notes", tags=["notes"])

class NoteRequest(BaseModel):
    title: str
    content: str

@router.get("")
def get_notes(current_user: dict = Depends(get_current_user)):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, title, content, created_at FROM notes WHERE user_id = %s",
                (current_user["user_id"],),
            )
            notes = cur.fetchall()
    return [dict(note) for note in notes]

@router.post("", status_code=201)
def create_note(body: NoteRequest, current_user: dict = Depends(get_current_user)):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO notes (title, content, user_id)
                VALUES (%s, %s, %s)
                RETURNING id, title, content, created_at
                """,
                (body.title, body.content, current_user["user_id"]),
            )
            note = cur.fetchone()
            conn.commit()
    return dict(note)

@router.delete("/{note_id}")
def delete_note(note_id: str, current_user: dict = Depends(get_current_user)):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM notes WHERE id = %s AND user_id = %s RETURNING id",
                (note_id, current_user["user_id"]),
            )
            deleted = cur.fetchone()
            conn.commit()

    if deleted is None:
        raise HTTPException(status_code=404, detail="Note not found")

    return {"message": "Note deleted successfully"}


@router.post("/{note_id}/summarize")
def summarize_note(note_id: str, current_user: dict = Depends(get_current_user)):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT title, content FROM notes WHERE id = %s AND user_id = %s",
                (note_id, current_user["user_id"]),
            )
            note = cur.fetchone()

    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")

    prompt = f"Summarize this note.\nTitle: {note['title']}\nContent: {note['content']}"

    # TODO: replace with real LLM call
    summary = "This is a placeholder summary of the note."

    return {"summary": summary}