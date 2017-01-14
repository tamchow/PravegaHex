Folder organisation and question structure:

1. A top-level folder called "Questions".
2. "Questions" will have subfolders for each question, each subfolder will be named as "Question #". ('#' denotes a number)
3. Each subfolder will have 5 files: 
	3.1. 1 for the question, called "Question.html" and formatted as HTML (Just put text inside the <BODY></BODY> tags of the sample documents)
	3.2. 4 for the answer options, each denoted as "Answer #.html", where # ranges from 1 to 4. Answers are also HTML-formatted.
	3.3. One answer file will be named as "Answer # - Correct Answer.html", which marks it as the correct answer. No special modifications to the document itself is required.
	
The Python program will display these in a window, with one label for the question, 4 buttons for the answers, and 1 button for pass, which discards the question from the list of available questions.
Once a question has been used, it can not be used again.

Relation to the Hex game:

Whenever a player clicks on an empty hex cell, they get shown the question window. The window remains open until dismissed using one of the available buttons. The question displayed is chosen randomly.

(Use screen mirroring to show the on-screen player content on the projector.)

Screen extension will be used between the players, as each of their Hex games will show up in separate windows on different screens, mediated by the "SpaceDesk" software.

Questions will show up on both player screens at the same time, and also the game windows will be duplicates of each other; so any of the player screens can be mirrored to the projector.

A correct answer will mark the selected cell with the player's color, and dismiss the question window, and pass the turn on to the next player.

A pass will dismiss the question window and pass the turn on to the next player.

A wrong answer will dismiss the question window, unmark (make blank) a random cell marked with the player's color, and pass the turn on to the next player.

All the dismissals of a question will consume it, implying that it will not be displayed again.

Considering all the above facts, I guess we should have some 50+ small questions handy, to be on the safe side ( there are 36 hex cells on a 6x6 Hex grid, which is the one we'll use).