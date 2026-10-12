"""Student Grade Calculator — простое веб-приложение для демонстрации PaaS."""
import os

from flask import Flask, render_template, request
from werkzeug.exceptions import NotFound
from werkzeug.middleware.dispatcher import DispatcherMiddleware

app = Flask(__name__)
PASS_SCORE = 50  # минимальный средний балл для зачёта

# Секретная ссылка: если задан URL_PREFIX, приложение доступно только по /<prefix>/, остальное — 404
URL_PREFIX = os.environ.get("URL_PREFIX", "").strip("/")
if URL_PREFIX:
    app.wsgi_app = DispatcherMiddleware(NotFound(), {"/" + URL_PREFIX: app.wsgi_app})


def calculate(test1, test2, exam):
    average = round((test1 + test2 + exam) / 3)
    return average, "PASS" if average >= PASS_SCORE else "FAIL"


@app.route("/", methods=["GET", "POST"])
def index():
    form, result, error = {}, None, None
    if request.method == "POST":
        form = request.form
        try:
            name = form.get("name", "").strip()
            scores = [float(form[k]) for k in ("test1", "test2", "exam")]
            if not name:
                raise ValueError("Введите имя студента")
            if any(not 0 <= s <= 100 for s in scores):
                raise ValueError("Оценки должны быть от 0 до 100")
            average, status = calculate(*scores)
            result = {"name": name, "average": average, "status": status}
        except (KeyError, ValueError) as e:
            error = str(e) if str(e) and "could not convert" not in str(e) else "Введите числа от 0 до 100"
    return render_template("index.html", form=form, result=result, error=error, pass_score=PASS_SCORE)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
