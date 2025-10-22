from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from .ai_service import pet_answer

@require_http_methods(["GET", "POST"])
def chat(request):
    # reset chat if ?new=1
    if request.GET.get("new") == "1":
        request.session["history"] = []
        request.session.modified = True
        return redirect("chat")
    
    #keep a tiny convo history in session
    history = request.session.get("history", [])

    if request.method == "POST":
        user_msg = (request.POST.get("message") or "").strip()
        if not user_msg:
            return render(request, "chat/chat.html", {"history": history, "error": "Please type a question."})
        
        # Append user message
        history.append({"role": "user", "text": user_msg})

        # real AI answer
        bot_reply = pet_answer(user_msg)
        
        history.append({"role": "bot", "text": bot_reply})

        # save back to session
        request.session["history"] = history
        request.session.modified = True

        return redirect("chat")
    
    return render(request, "chat/chat.html", {"history": history})