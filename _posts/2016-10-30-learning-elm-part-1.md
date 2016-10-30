---
layout: post
title: Learning Elm - Part 1
tags: elm, learning
---

I decided to try [Elm] yesterday but after spending a couple of hours, a bit frustrated after feeling I'm not going anywhere. Everywhere on the web people are praising Elm as easy to learn, even a 4th grader manage to build a simple games in just few hours, and I'm still glaring trying to understand the button examples from the docs.

The button example is quite simple, you have 2 buttons that when clicked, will increment or decrement a single value (model). The code look like this:-

```elm
import Html exposing (Html, button, div, text)
import Html.App as Html
import Html.Events exposing (onClick)



main =
  Html.beginnerProgram
    { model = model
    , view = view
    , update = update
    }



-- MODEL


type alias Model = Int


model : Model
model =
  0



-- UPDATE


type Msg
  = Increment
  | Decrement


update : Msg -> Model -> Model
update msg model =
  case msg of
    Increment ->
      model + 1

    Decrement ->
      model - 1



-- VIEW


view : Model -> Html Msg
view model =
  div []
    [ button [ onClick Decrement ] [ text "-" ]
    , div [] [ text (toString model) ]
    , button [ onClick Increment ] [ text "+" ]
    ]
```
This code work perfectly when I try with `elm-reactor`. It's a good start. So I start to change it a bit by adding a reset button that will reset the model value back to 0. As claimed in the docs, it work quite intuitively, I managed to get around it even without fully understanding the core language yet.

```
diff --git a/button2.elm b/button2.elm
index a505170..5b20f65 100644
--- a/button2.elm
+++ b/button2.elm
@@ -31,6 +31,7 @@ model =
 type Msg
   = Increment
   | Decrement
+  | Reset


 update : Msg -> Model -> Model
@@ -42,6 +43,8 @@ update msg model =
     Decrement ->
       model - 1

+    Reset ->
+      0


 -- VIEW
@@ -53,4 +56,5 @@ view model =
     [ button [ onClick Decrement ] [ text "-" ]
     , div [] [ text (toString model) ]
     , button [ onClick Increment ] [ text "+" ]
+    , button [ onClick Reset ] [ text "Reset" ]
     ]
```
Actually it not quite straightforward as originally I try to this instead when reseting the model value back to 0:-

```
    Reset ->
      model = 0
```
And the compiler complained:-

```
Detected errors in 1 module.


-- SYNTAX PROBLEM -------------------------------------------------- button2.elm

I ran into something unexpected when parsing your code!

47|       model = 0
                ^
I am looking for one of the following things:

    end of input
    whitespace
```
I got pass through that after a couple of try and error. I think the error message will be more helpful if it say something like *"assignment is not allowed here"*, *"Reassigning value not allowed"*, or *"Mutating value not allowed here"*.

Now I got passed the first challenge, I started thinking what if I have 2 value to update when the button clicked ? So I defined `model2`:-

```
+model2 : Model
+model2 =
+  0
```

But I don't know how to pass the `model2` value into the `update` function. After googling around, I ended up defining a `record` model instead.

```
--- a/button2.elm
+++ b/button2.elm
 -- MODEL


-type alias Model = Int
+type alias Model = { one: Int, two: Int }


 model : Model
 model =
-  0
-
+  { one = 0, two = 0 }


 -- UPDATE
@@ -31,17 +30,20 @@ model =
 type Msg
   = Increment
   | Decrement
+  | Reset


 update : Msg -> Model -> Model
 update msg model =
   case msg of
     Increment ->
-      model + 1
+      { model | one = model.one + 1 }

     Decrement ->
-      model - 1
+      { model | one = model.one - 1 }

+    Reset ->
+      { model | one = 0, two = 0 }


 -- VIEW
@@ -51,6 +53,8 @@ view : Model -> Html Msg
 view model =
   div []
     [ button [ onClick Decrement ] [ text "-" ]
-    , div [] [ text (toString model) ]
+    , div [] [ text (toString model.one) ]
+    , div [] [ text (toString model.two) ]
     , button [ onClick Increment ] [ text "+" ]
+    , button [ onClick Reset ] [ text "Reset" ]
     ]
```
It look easy here but I don't know how to explain how hard it is to get up until this state. Figuring the syntax how to update the record ... sigh. Using record work now but it still no different that the original example. I can't update `model.two` value when any button was clicked. My first attempt was to add code that updating `model.two` outside the `case` block. 

```
--- a/button2.elm
+++ b/button2.elm
@@ -45,6 +45,8 @@ update msg model =
     Reset ->
       { model | one = 0, two = 0 }

+  { model | two = model.two + 10 }
+

 -- VIEW
```

Adding the line before the `case` block also didn't work. It look like only single expression is allowed in the function body, I don't know. Of cource I can update `model.two` in all of the conditions but that look a lot of repeatition and against DRY. At this point, I started to give up and call it a day.

This morning, I try to look at it again. Watch a couple of videos and try to think from different angle. Already join Elm Slack group since I think maybe just asking will lead me to the right direction instead of banging in the dark like this.

I think about functional programming, changing state and side effect. So probably what I'm trying to do yesterday - changing `model.two` value outside the `case` block was a side effect. FP is about calling function, pass a parameter and get back a result. So maybe I need to define another function that receive the updated `model.one`, and then update `model.two` inside that function. So I ended up with this code:-

```
import Html exposing (Html, button, div, text)
import Html.App as App
import Html.Events exposing (onClick)


main =
  App.beginnerProgram { model = model, view = view, update = update }


-- MODEL

type alias Model = { one: Int, two: Int }

model : Model
model =
  { one = 0, two = 10 }


-- UPDATE

type Msg = Increment | Decrement | Reset

update2 : Model -> Model
update2 model =
    { model | two = model.two + 10 }

update : Msg -> Model -> Model
update msg model =
  case msg of
    Increment ->
      update2 { model | one = model.one + 1 }

    Decrement ->
      update2 { model | one = model.one - 1 }

    Reset ->
      { model | one = 0, two = 0 }

-- VIEW

view : Model -> Html Msg
view model =
  div []
    [ button [ onClick Decrement ] [ text "-" ]
    , div [] [ text (toString model.one) ]
    , div [] [ text (toString model.two) ]
    , button [ onClick Increment ] [ text "+" ]
    , button [ onClick Reset ] [ text "Reset" ]
    ]
```
So now doesn't matter which button clicked, `model.two` always incremented by 10. Not sure if this the correct solution but at least I got it moving.

[Elm]: http://elm-lang.org/
