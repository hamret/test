from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import pandas as pd
from deep_translator import GoogleTranslator

app = FastAPI()
templates = Jinja2Templates(directory="templates")
FILE_PATH = 'mainfiles.csv'

try:
    df = pd.read_csv(FILE_PATH, encoding='euc-kr')
    df_unlabeled = df[df['label'].isnull()].reset_index(drop=True)
    if not df_unlabeled.empty:
        current_index = 0
    else:
        current_index = -1  # 라벨링 완료 상태
except FileNotFoundError:
    df_unlabeled = pd.DataFrame()
    current_index = -2  # 파일 없음 오류
except Exception as e:
    df_unlabeled = pd.DataFrame()
    current_index = -3  # 기타 오류


def get_current_data():
    if 0 <= current_index < len(df_unlabeled):
        english_text = df_unlabeled.loc[current_index, 'text']
        try:
            korean_translation = GoogleTranslator(source='en', target='ko').translate(english_text)
        except Exception:
            korean_translation = "(번역 실패)"
        return {'index': current_index, 'original': english_text, 'translated': korean_translation}
    elif current_index == -1:
        return {'message': '모든 데이터 라벨링이 완료되었습니다.'}
    elif current_index == -2:
        return {'error': 'CSV 파일을 찾을 수 없습니다.'}
    elif current_index == -3:
        return {'error': f'파일 처리 중 오류가 발생했습니다: {str(e)}'}
    else:
        return {}


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    data = get_current_data()
    return templates.TemplateResponse("22.html", {"request": request, "data": data})


@app.post("/save_label")
async def save_label(request: Request):
    global current_index
    try:
        body = await request.json()  # JSON 데이터를 읽어옵니다.
        label = body.get("label")
        if 0 <= current_index < len(df_unlabeled) and label:
            df.loc[df_unlabeled.index[current_index], 'label'] = label
            current_index += 1
            try:
                df.to_csv(FILE_PATH, index=False, encoding='euc-kr')
                return RedirectResponse("/", status_code=303)  # 저장 후 메인 페이지로 리다이렉트
            except Exception as e:
                return {"status": "error", "message": f"CSV 저장 오류: {str(e)}"}
        else:
            return {"status": "error", "message": "라벨 저장에 실패했습니다."}
    except Exception as e:
        return {"status": "error", "message": f"요청 처리 중 오류 발생: {str(e)}"}
