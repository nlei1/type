# Type APP: DESIGN.md
## Destination 1: Login, the Registrar, and the Preview Page
This project was incredibly easy to implement. Login and register work like they would on most Flask apps, they query using sqlite commands and return an error if something goes wrong. When implementing this section, I didn’t have to make much design decisions other than thinking about how to structure the sqlite database. If you navigate the typeapp.db SQLite GUI, you will be able to see how the table called users has 3 columns: id (unique identifier for user), username, and hashed password. I decided to have a unique automatically enumerated ID identifier for each user because it makes it easier to link to other tables in the db.

Once you have successfully signed in, you will see the preview page that shows users their progress and more specifically, their most recent drafts of every pagraprag. I decided to have this as the index.html as it is important for users coming back to see what progress they have so far. Implementing this was quite simple, too. Frontend-wise, I used Bootstrap’s linked group component that allows users to toggle which section they would like to see. Backend-wise, I used a sqlite command to show the most recent drafts:

```python
db.execute("SELECT id, topic, content FROM paragraphs WHERE user=? ORDER BY id", session["user_id"])
```

## Destination 2: Paragraph adder and typewriter
These are the primary features of my ‘modern typewriter’. I spent the most design time thinking about how to optimize and simplify the experience for procrastinative users to write their essay. In the end, I chose to have the paragraph adder and writer features on separate pages, as this would help users break up their ideas into smaller pieces that would be easier to concentrate on. Regarding user interfaces, I decided to implement quite minimalistic frontend components for these two features. For paragraph adder, I decided to use a one line form with a button; in terms of typewriter, I implemented a drop down menu with a multi line typearea that could expand. Designing these two features, I also spent some time thinking about how to best implement the database tables. Ultimately, I decided to create two new tables:

    paragraphs
    history

The former table has 4 columns: an automatically enumerating id, the id of the user, the name of the paragraph topic, and content, which stores a default placeholder of ‘temp placeholder. I will cover the latter table in the next destination.

Everytime a user adds a new paragraph topic or writes the content of one application.py queries out a SQLite command that updates and adds a new row to the two tables


## Destination 3: Version Control
Now, as I mentioned when we were visiting Destination 2, I implemented the table called

    history

for the Version Control feature.

I decided to create this features for two reasons. First, I would like to have a page for users to see the previous drafts of their paragraph; in case they think they like a previous draft better, they could just come back here and copy the previous draft and paste it into the typewriter. Secondly, personally I think that having a progress page makes users feel more satisfied by the writing process—it makes users feel more productive.

Both frontend and backend of this feature were easy to implement. In terms of backend, I used a sqlite query to select all of the entries (rows, that is) in history that has the user_id of the current user’s. Frontend-wise, I used a Bootstrap table to display every row from the selected table. The background of the row changes color when a user hovers over it; I accomplished this using the Bootstrap table-hover class in my version.html file.



## Destination 4: Stats
I learned the most while building the components you see at this destination. 

At the top of the Stats page, you can see that there is a polished up version of everything you see in the preview page, combined. I accomplished this by using a SQLite query that selects all of the user’s most recent paragraph drafts. I then stored all of the paragraphs into one single python variable.

Underneath, you can see a copy onto the clipboard feature. I completed this feature in JS, which you can find in the script section of layout.html, after going through a tutorial on this provided by W3Schools. 

Underneath Copy and Go, you can find key statistics about your writing. Firstly, there is a section telling you what language it thinks your essay is written in, as well as how confident the tool is in determining the language of your writing. I did this by calling the detect language API. At the top of my application.py file, you can see how I configured this API. Since I won’t be putting this web app on the internet, I just simply put my API key in there to save time. If you scroll back to the stats method in application.py, you can see that I passed in the combined essay into the API call, and in frontend used attributes of the JSON object to display the language, confidence, and reliability. 

I utilized the similar process when implementing the sentiments and subjectivity section. This time, though, I actually configured the API inside helpers.py, as this API is more complicated to use. Originally, I wanted to use the Deep Learning and Profanity detection services the API provides. After finding out that that would use more API calls than I could afford, I decided to simply stick to more subjectivity and sentiments features. If I continue to work on this project and allocate budget to this, I would consider paying for the premium of this API and using the Deep Learning features. 

Lastly, in this destination, you can see a section showing readability related statistics. I did this by using the textstat library. I learned how to use methods from a library while completing this section.


## Destination 5: Social media land
While working on building the social media feature of my typewriter app, I created a new table in my database, called social which has 4 columns: the social media post id, the id of the user, the content of the post, and the automatically generated timestamp.

Everytime the user posts a social media status update, a row gets added to the social table:
```python
db.execute("INSERT INTO social (username, content) VALUES(?, ?)", username[0]['username'], request.form.get("topic"))
```
Then, when displaying the social page, the program selects every single social media post in social.db and passes it to the front end:
```python
db.execute("SELECT username, content, timemstamp FROM social ORDER BY timemstamp DESC")
```