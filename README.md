<h1> Queuesome </h1>

   A Django Web Application Powered By Spotipy

   Try it yourself at <a href="https://queuesome.com">queuesome.com</a>



   <h3>What is It?</h3>

   Queuesome is a Fun and Interactive way to Listen to Music Together

   Take Turns Selecting and Creating Different Song Categories

   Pick Songs that Fit Each Category

   Listen to Everyone's Picks and Give Likes to the Songs that Fit the Best 

   While you Listen, Continue to Select Categories, Pick Songs, and Give Out Likes to the Best Picks



   <h3> Set Up Local Dev </h3>
   
   Requires Python 3.7 or Higher

   <h4>Create Virtual Environment</h4>

   In Desired Directory Run

   <I>python -m venv venv</I>


   <h4>Activate Virutal Environment</h4>
 
   <I>C:\> venv\Scripts\activate.bat</I>


   <h4> Install Dependencies </h4>

   <I>pip install -r requirements.txt</I>


   <h4> Edit <I>queue_it_up/settings.py</I> </h4>

   line 17: HEROKU = False

   line 90: Configure Local Database

   line 177: YOUR-SPOTIFY-CLIENT-ID


   <h4> Add The Following Environment Variables </h4>

   You can also hardcode your own values. Line numbers refer to <I>queue_it_up/settings.py</I>

   line 27: DJANGO_SECRET_Q

   line 175: SPOTIFY_CLIENT_SECRET

   line 178: SYSTEM_USER_ID


   <h4> Migrate Database </h4>

   <I>python manage.py makemigrations</I>

   <I>python manage.py migrate</I>


   <h4> Collect Static Images </h4>

   <I>python manage.py collectstatic</I>


   <h4>Add Categories via Python Shell</h4>

   Open the Python Shell by Entering:

   <I>python manage.py shell</I>

   Paste the Following code with new Categories in the cats list

   <I>from party.models import Library</I>

   <I>cats = ["new cat1", "new cat2"]</I>

   <I>for x in cats:</I>
       <I>l = library(name = x)</I>
       <I>l.save()</I>


   <h4> Run Server </h4>

   <I>python manage.py runserver</I>

   visit <a href="http://localhost:8000">http://localhost:8000</a> to view application


   <h4>To Create Access to other Devices from Your IP Address</h4>

   Edit queue_it_up/settings.py and add IP address to ALLOWED_HOSTS

   <I>python manage.py runserver 0.0.0.0:<PORT></I>
   
   
   <h3> Edit Spotify Developer Settings </h3>
   
   Under Edit Settings Add
   
   http://localhost:8000/party/auth/
   
   OR
   
   http://YOUR_IP:YOUR_PORT/party/auth/
   
   to Redirect URI's





