from channels.generic.websocket import AsyncJsonWebsocketConsumer
from .models import Question

from channels.generic.websocket import WebsocketConsumer
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from .models import *
from asgiref.sync import sync_to_async
import json, asyncio
from django.db.models import F



class QuizConsumer(AsyncJsonWebsocketConsumer):
    # Connect only runs when socket runs 
    # self.attempt will stored on the WebSocket consumer instance. if only attmept then it has only life in the connect() local scope
    async def connect(self):

        #We defined the path in the routing.py, When a WebSocket connects, Channels gives you a dictionary called scope, in which we store the parameter given at last to use it later
        self.quiz_id = self.scope['url_route']['kwargs']['quiz_id']
        self.user = self.scope['user']
    
        # We will only fetch the attempt here, new attempt will be created and question_order will be created inside views.py
        self.quiz = await sync_to_async(Quiz.objects.get)(quiz_id=self.quiz_id)
        self.attempt = await sync_to_async(Attempt.objects.get)(
            user=self.user,
            quiz=self.quiz
        )
        


        
        self.question_index = self.attempt.current_question_index
        # Stores the Question IDs
        self.questions = self.attempt.question_order
 
        # if self.attempt.end_time == None:
        #     print("Set end time in the consumers.py")
        #     self.attempt.end_time = now() + self.quiz.time_limit
        #     await sync_to_async(self.attempt.save)(update_fields=['end_time'])


        if self.attempt.remaining_time > 0 and now() < self.attempt.end_time:
            # Accept the Websocket
            await self.accept()
            await self.send_json({
                "type" : "time",
                "remaining_time": int(self.attempt.remaining_time),
            })
            print("Connected OK")

        else:
            self.end_quiz()
            await self.close()

        self.fullscreen_violations = 0
        # Rebuild local_answers during reconnect
        pre_answers = await sync_to_async(list)(
            Answer.objects.filter(attempt=self.attempt)
            .select_related('question')
        )
        self.local_answers = {}

        for ans in pre_answers:
            q = ans.question

            # Only MCQ / True-False kept in cache
            #if q.question_type in ["mcq", "true_false"]:

            # Find question index in the ordered question list
            try:
                question_index = self.questions.index(q.question_id)
            except ValueError:
                continue  # safety: shouldn't happen

            # Find the selected option index
            try:
                if q.question_type == 'text':
                    answer = ans.text_answer
                    self.local_answers[question_index] = answer
                else:
                    option_index = q.options.index(ans.selected_option)
                    self.local_answers[question_index] = option_index

            except ValueError:
                option_index = None  # option removed/changed

            # Save in memory cache

        # if reconnected 
        self.review_but_answered = self.attempt.review_but_answered or []
        print("Review answers are ",self.review_but_answered)
        self.review_not_answered = self.attempt.review_not_answered or []
        if self.review_but_answered or self.review_not_answered or self.local_answers:
            await self.send_json({
                "type": "reload_answers",
                "review_but_answered": self.review_but_answered,
                "review_not_answered": self.review_not_answered,
                "local_answers": list(
                    set(self.local_answers.keys()) - set(self.review_but_answered)
                )

            })


        await self.send_question()
        await self.send_answer()


        # ❌ BAD
        # await asyncio.sleep(x) inside connect()
        # → connect never returns, receive_json never triggers.

        # ✔ GOOD

        # asyncio.create_task() schedules sleep in background
        # → connect returns immediately
        # → consumer is free to receive messages
        # → receive_json works instantly
        
        self.timer = asyncio.create_task(self.timer_task())

    async def timer_task(self):
        try:
            if self.attempt.remaining_time > 0:
                await asyncio.sleep(self.attempt.remaining_time)

            # Reload attempt status to avoid ending twice
            await sync_to_async(self.attempt.refresh_from_db)()
            if self.attempt.completion_reason != "manual_submit":
                await self.end_quiz()

        finally:
            await self.close()

    async def end_quiz(self, reason="timeout"):
        await sync_to_async(self.attempt.finalize)(reason)

        # Tell the frontend to redirect
        await self.send_json({
            "type": "redirect",
            "url": f"/quiz_submission/{self.attempt.attempt_id}/"
        })

    async def send_answer(self):
        answer = self.local_answers.get(self.question_index)  # returns None if not found
        print("Question index is ", self.question_index)
        print("Before sending the question local answer = ", self.local_answers)
        if answer is not None:
            await self.send_json({
                "type":"saved_answer",
                "answer":answer
            })
            print("Answer sent to frontend",answer)



    async def receive_json(self, content):

        action = content.get("action")
        if action == "navigate" and self.question_index!= content["index"]:
            self.question_index = content["index"]
            print("Index Changed")

            await self.send_question()
            await self.send_answer()

            
        elif action == "previous" and self.question_index>0:
            self.question_index -= 1
            await self.send_question()
            await self.send_answer()

            print("received previous")
        elif action in ["next","review"] :
            print("received next")
            # user answer received
            # More clever way is to save only indexes of the option the user selected, it will decrease evaluation time. We can compare the correct index to selected index.
            
            user_answer = (content.get("answer")) #If answer=None we can strip None; so we strip ""
            print("Received answer from frontend:", user_answer, "for Q index", self.question_index)

            if self.question_index in self.review_but_answered:
                self.review_but_answered.remove(self.question_index)

            if user_answer is not None and user_answer !='':
                if self.question.question_type in ['mcq','true_false']:
                    if user_answer in self.question.options:
                        self.local_answers[self.question_index] = self.question.options.index(user_answer)
                    # else:
                    #     # If answer not valid for this question, clear or set None
                    #     self.local_answers[self.question_index] = None
                else:
                    self.local_answers[self.question_index] = user_answer

            if user_answer is not None and user_answer != '':
                
                # Case 1: MCQ question
                if self.question.question_type in ['mcq', 'true_false']:
                    if user_answer in self.question.options:
                        self.local_answers[self.question_index] = self.question.options.index(user_answer)
                    else:
                        # Ignore invalid answer, do NOT store
                        self.local_answers[self.question_index] = None

                # Case 2: Text question
                else:
                    # If answer looks like an MCQ option index → ignore it
                    if isinstance(user_answer, str) and not user_answer.isdigit():
                        self.local_answers[self.question_index] = user_answer.strip()
                    else:
                        # Ignore invalid text answer
                        self.local_answers[self.question_index] = None

                await sync_to_async(Answer.objects.update_or_create)(
                    answered_by=self.user,
                    question=self.question,
                    quiz=self.quiz,
                    attempt=self.attempt,
                    defaults={'text_answer': (user_answer.strip() or "") if self.question.question_type == 'text' else None,
                            'selected_option': user_answer if self.question.question_type in ['mcq', 'true_false'] else None}
                )
                print("Answer saved successfully")
                user_answer = None # Reset the user_answer else it will store the same answer if you do not answer the next question
            
            if self.question_index<len(self.questions) -1:
                # Move to next question
                self.question_index += 1
                await self.send_question()
                await self.send_answer()

            review_status = content.get("subtype")
            review_question_index = self.question_index -1 # Store the index 
            if review_status == "answered":
                if review_question_index not in self.review_but_answered:
                    self.review_but_answered.append(review_question_index)
                if review_question_index in self.review_not_answered:
                    self.review_not_answered.remove(review_question_index)

            elif review_status == "unanswered":
                if review_question_index not in self.review_not_answered:
                    self.review_not_answered.append(review_question_index)
                if review_question_index in self.review_but_answered:
                    self.review_but_answered.remove(review_question_index)

            
 
        elif action == "clear":
            question_id = self.questions[self.question_index]
            #sync_to_async expects a callable, not the result of the operation.
            await sync_to_async(
                lambda: Answer.objects.filter(question_id=question_id, attempt=self.attempt).delete()
            )()

            if self.question_index in self.review_not_answered:
                self.review_not_answered.remove(self.question_index)

            # remove local cached answer
            if self.local_answers.get(self.question_index):
                del self.local_answers[self.question_index]
            print("received clear")

        elif action == "review":
            print("received review")

        elif action == "fullscreen_exit":
            self.fullscreen_violations +=1
            #print("Fullscreen Violations = ",self.fullscreen_violations)
            if self.fullscreen_violations > 300:
                await self.end_quiz()

        elif action == "reload":
            print("In reload")

            await sync_to_async(
                Attempt.objects.filter(attempt_id=self.attempt.attempt_id).update
            )(reload=F("reload") + 1)

            # Refresh instance from DB
            await sync_to_async(self.attempt.refresh_from_db)()

            if self.attempt.reload >= 300:
                await self.end_quiz(reason="cheating")




    #based on the close_cide we can either deduct some time or do nothing
    async def disconnect(self, close_code):
        # Cancel backend timer if it exists
        if hasattr(self, "timer") and not self.timer.cancelled():
            self.timer.cancel()

        # Reload attempt to ensure latest status
        await sync_to_async(self.attempt.refresh_from_db)()

        # If quiz already ended or submitted manually → do NOT save anything
        if self.attempt.completion_reason == "manual_submit":
            return


        # Here the logic is wrong, even the user submit the quiz manually is neding but remainning time is still saving and 
        # for reconnect we check for remaing time, where are we redirecting to submission page ?
        
        # Calculate remaining time
        remaining = (self.attempt.end_time - timezone.now()).total_seconds()

        # Save remaining time in Attempt
        self.attempt.remaining_time = max(0, remaining)
        self.attempt.current_question_index = self.question_index

        # Before Disconnect save this
        self.attempt.review_but_answered =  self.review_but_answered
        self.attempt.review_not_answered = self.review_not_answered

        await sync_to_async(self.attempt.save)(update_fields=['remaining_time', 'current_question_index','review_not_answered','review_but_answered'])

    # question_index here also starts from 0
    # 

    async def send_question(self):
        question_id = self.questions[self.question_index]
        self.question = await sync_to_async(
            lambda: Question.objects.get(question_id=question_id)
        )()

        #Lambda because sync_to_async expects a callable (a function), not the result of a function.
        # If we direct form a get without lambda it will run immediately error SynchronousOnlyOperation in aysnc context → database access happens in async context
        # Using lambda, now it is a function that will only run later — inside the thread used by sync_to_async.


        #Shuffle options 
        await self.send_json({
            "type": "question",
            "data": {
                "subtype":self.question.question_type,
                "index": self.question_index,
                "id": self.question.question_id,
                "text": self.question.question_text,
                "options": self.question.options,
                "image_url": self.question.question_image.url if self.question.question_image else None
            }
        })
        print("send question index ", self.question_index)


