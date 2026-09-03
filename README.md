<h1> Queuesome </h1>

   A Django Web Application Powered By Spotipy

   See how it works at <a href="https://www.queuesome.com/tutorial">queuesome.com</a>



   <h3>What is It?</h3>

   Queuesome is a Fun and Interactive way to Listen to Music Together

   Take Turns Selecting and Creating Different Song Categories

   Pick Songs that Fit Each Category

   Listen to Everyone's Picks and Give Likes to the Songs that Fit the Best 

   While you Listen, Continue to Select Categories, Pick Songs, and Give Out Likes to the Best Picks



   <h3> Set Up Local Development </h3>

   Queuesome requires Python 3.13 and PostgreSQL. Docker is used for the local
   database so developers do not need to install or configure PostgreSQL
   directly.
   
   <h4>Create Virtual Environment</h4>

   In Desired Directory Run

   <I>python -m venv venv</I>


   <h4>Activate Virtual Environment</h4>
 
   <I>C:\> venv\Scripts\activate.bat</I>


   <h4> Install Dependencies </h4>

   <I>pip install -r requirements.txt</I>


   On macOS or Linux: <I>source venv/bin/activate</I>


   <h4>Start PostgreSQL</h4>

   <I>docker compose up -d db</I>


   <h4>Configure the Environment</h4>

   Copy <I>.env.example</I> to <I>.env</I> and add your Spotify credentials.
   Django does not automatically load this file, so export the values in your
   shell or configure them through your IDE. The defaults in
   <I>queue_it_up/settings.py</I> connect to the Docker database above.


   <h4> Migrate Database </h4>

   <I>python manage.py migrate</I>


   <h4> Collect Static Images </h4>

   <I>python manage.py collectstatic --noinput</I>


   <h4>Run Checks and Tests</h4>

   <I>python manage.py check</I>

   <I>python manage.py makemigrations party blog spot --check --dry-run</I>

   <I>python manage.py test</I>


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




