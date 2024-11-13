from datetime import date, timedelta, datetime
from fastapi import APIRouter, HTTPException, Depends, Query, Response, status, Request, Form
from app.utils.user import  get_user_id
from app.models import Response_Model
from app.models.user import User
from app.models.fc import Flashcard
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.responses import JSONResponse, RedirectResponse

from app.utils.ai import GenerateStory, GenerateVoice, get_completion

api = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@api.get("/flashcards/", response_model=Response_Model, response_class=JSONResponse) # response_class=HTMLResponse
async def get_flashcard_html(
    response: Response,
    request: Request,
    uid: str = Depends(get_user_id)
):
    """
    Retrieve flashcards due for review today for the authenticated user.
    """
    try:
        today = date.today()
        user = await User.get(uid)  # Temporary: for UI purpose
        username = user.username  # Temporary: for UI purpose
        print(type(username))
        flashcard = await Flashcard.find_one(Flashcard.user_id == username, Flashcard.review_date >= today) # >=
        count = await Flashcard.find(Flashcard.user_id == username, Flashcard.review_date >= today).count() # <=
        # count = await Flashcard.find((Flashcard.user_id == username) & (Flashcard.review_date >= today())).to_list()
        print(flashcard)
        # Build the response data
        data = {
            "success": True,
            "message": "Flashcard retrieved successfully",
            "data": dict(count=count, flashcard=flashcard)
        }
        response.status_code = status.HTTP_200_OK
    except HTTPException as e:
        data = {'success': False, 'message': e.detail, 'data': None}
        response.status_code = e.status_code
    except Exception as e:
        data = {'success': False, 'message': str(e), 'data': None}
        response.status_code = status.HTTP_406_NOT_ACCEPTABLE
    # return templates.TemplateResponse("flashcards.html", data["data"])
    return data


@api.post("/add_flashcard/")
async def add_flashcard(
    response: Response,
    question: str = Form(...),
    answer: str = Form(...),
    uid: str = Depends(get_user_id)
    ):
    try:
        user = await User.get(uid)
        flashcard = Flashcard(
            user_id=user.username,
            question=question,
            answer=answer,
            review_date=datetime.now().date() + timedelta(days=1),
            level=2
        )
        await flashcard.create()
        data = {
            "success": True,
            "message": "Flashcard created successfully",
            "data": flashcard
        }
        response.status_code = status.HTTP_201_CREATED
        # return RedirectResponse(url=f"/flashcards/", status_code=303) #Temporary 
    except HTTPException as e:
        data = {'success': False, 'message': e.detail, 'data': None}
        response.status_code = e.status_code
    except Exception as e:
        data = {'success': False, 'message': str(e), 'data': None}
        response.status_code = status.HTTP_406_NOT_ACCEPTABLE
    return data

@api.get("/generate_story/")
async def generate_story(
    response: Response,
    request: Request,
    uid: str = Depends(get_user_id)
):

    try:
        user = await User.get(uid)
        username = user.username
        print(username)
        questions_list = await Flashcard.find(Flashcard.user_id == username).to_list()
        questions = [doc.question for doc in questions_list]
        print(questions)

        if len(questions) < 10:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Not enough questions in the database."
            )

        story_text = GenerateStory(questions, 6)
        audio_path = f"app/static/audio/story_audio_{username}.mp3"
        GenerateVoice(audio_path, story_text)

        data = {
            "success": True,
            "message": "Story generated successfully",
            "data": {
                "story": story_text,
                "audio_path": f"/{audio_path}"
            }
        }
        response.status_code = status.HTTP_200_OK
    except HTTPException as e:
        data = {'success': False, 'message': e.detail, 'data': None}
        response.status_code = e.status_code
    except Exception as e:
        data = {'success': False, 'message': str(e), 'data': None}
        response.status_code = status.HTTP_406_NOT_ACCEPTABLE
    return data

@api.post("/answer/{flashcard_id}")
async def answer(
    response: Response,
    flashcard_id: str,
    correct: str = Form(...),
    uid: str = Depends(get_user_id)
):
    print(333333)
    try:
        user = await User.get(uid)
        username = user.username
        print(flashcard_id)
        flashcard = await Flashcard.get(flashcard_id)
        print(flashcard)
        if flashcard.user_id != username:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this flashcard"
            )
        if correct:
            new_level = flashcard.level + 1
            review_date = datetime.now().date() + timedelta(days=2**new_level - 1)
        else:
            new_level = 2
            review_date = datetime.now().date() + timedelta(days=1)

        print(2)
        await flashcard.update({
            "$set": {
                "level": new_level,
                "review_date": review_date
            }
        })

        data = {
            "success": True,
            "message": "Flashcard updated successfully",
            "data": flashcard
        }
        response.status_code = status.HTTP_200_OK
        # return RedirectResponse(url=f"/flashcards/", status_code=303) # Temprory
    except HTTPException as e:
        data = {'success': False, 'message': e.detail, 'data': None}
        response.status_code = e.status_code
    except Exception as e:
        data = {'success': False, 'message': str(e), 'data': None}
        response.status_code = status.HTTP_406_NOT_ACCEPTABLE
    return data


@api.get("/generate_answer/")
async def generate_answer(
    response: Response,
    question: str = Form(...),
    uid: str = Depends(get_user_id)
):
    try:
        answer = get_completion(question)

        data = {
            "success": True,
            "message": "Answer generated successfully",
            "data": {"answer": answer}
        }
        response.status_code = status.HTTP_200_OK
        return JSONResponse(content={"answer": answer}) # Temprory

    except HTTPException as e:
        data = {'success': False, 'message': e.detail, 'data': None}
        response.status_code = e.status_code
    except Exception as e:
        data = {
            'success': False,
            'message': "Reached the limit of AI usage for today",
            'data': None
        }
        response.status_code = status.HTTP_429_TOO_MANY_REQUESTS
    return data

@api.post("/edit_flashcard/{flashcard_id}")
async def edit_flashcard(
    response: Response,
    flashcard_id: str,
    edited_question: str = Form(...),
    edited_answer: str = Form(...),
    uid: str = Depends(get_user_id)
):
    try:
        flashcard = await Flashcard.get(flashcard_id)
        if flashcard.user_id != uid:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this flashcard"
            )

        await flashcard.update({
            "$set": {
                "question": edited_question,
                "answer": edited_answer
            }
        })

        data = {
            "success": True,
            "message": "Flashcard updated successfully",
            "data": flashcard
        }
        response.status_code = status.HTTP_200_OK
        return RedirectResponse(url=f"/flashcards/", status_code=303) # Temprory
    except HTTPException as e:
        data = {'success': False, 'message': e.detail, 'data': None}
        response.status_code = e.status_code
    except Exception as e:
        data = {'success': False, 'message': str(e), 'data': None}
        response.status_code = status.HTTP_406_NOT_ACCEPTABLE
    return data

@api.post("/delete_flashcard/{flashcard_id}")
async def delete_flashcard(
    response: Response,
    flashcard_id: str,
    uid: str = Depends(get_user_id)
):
    try:
        flashcard = await Flashcard.get(flashcard_id)
        if flashcard.user_id != uid:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this flashcard"
            )

        await flashcard.delete()

        data = {
            "success": True,
            "message": "Flashcard deleted successfully",
            "data": None
        }
        response.status_code = status.HTTP_200_OK
        return RedirectResponse(url=f"/flashcards/", status_code=303)
    except HTTPException as e:
        data = {'success': False, 'message': e.detail, 'data': None}
        response.status_code = e.status_code
    except Exception as e:
        data = {'success': False, 'message': str(e), 'data': None}
        response.status_code = status.HTTP_406_NOT_ACCEPTABLE
    return data