(set width    (input "NUMBER" "Width:  "))
(set height   (input "NUMBER" "Height: "))
(set max_iter (input "NUMBER" "Max Iterations: "))

# returns the absolute value of a number
(setf abs 1 1 '("NUMBER")
      '(ifelse (gt (get 0) 0) (get 0) (* -1 (get 0)))
)


# returns the character for the current coordinate
# scaled_x = (4*(x / width) - 2)
# scaled_y = (4*(y / height) - 2)
# c1 = 0
# c2 = 0
# while (abs(c1) < 2 && abs(c2) < 2 && iter < max_iter):
#     c1temp = c1*c1 - c2*c2 + scaled_x
#     c2 = 2*c1*c2 + scaled_y
#     c1 = c1temp
#     iter++
(setf get_char 2 2 '("NUMBER" "NUMBER") '(last
    (set scaled_x (- (*
         4
         (/ (get 0) (load width))
    ) 2))
    (set scaled_y (- (*
         4
         (/ (get 1) (load height))
    ) 2))
    (set c1 0)
    (set c2 0)
    (set iter 0)
    (while
       '(and
           (not (gt (abs (load c1)) 2))
           (not (gt (abs (load c2)) 2))
           (not (gt (load iter) (load max_iter)))
       )

       '(set c1temp
           (+ (-
               (* (load c1) (load c1))
               (* (load c2) (load c2))
           ) (load scaled_x))
       )
       '(set c2
           (+ (*
               2
               (load c1)
               (load c2)
           ) (load scaled_y))
       )
       '(set c1 (load c1temp))
       '(set iter (+ 1 (load iter)))
    )
    (ifelse (gt (load iter) (load max_iter))           "█"
    (ifelse (gt (load iter) (* 0.1 (load max_iter)))   "▓"
    (ifelse (gt (load iter) (* 0.05 (load max_iter)))  "▒"
    (ifelse (gt (load iter) (* 0.025 (load max_iter))) "░"
                                                       " "
    ))))
))

(setf draw_line 1 1 '("NUMBER") '(last
      (set result "")
      (set x 0)
      (while '(lt (load x) (load width))
             '(set result (concat (load result)
                   (get_char (load x) (get 0))
             ))
             '(set x (+ 1 (load x)))
      )
      (load result)
))

(setf draw 0 0 '() '(last
      (set y 0)
      (while '(lt (load y) (load height))
             '(print (draw_line (load y)))
             '(set y (+ 1 (load y)))
      )
))

(draw)
