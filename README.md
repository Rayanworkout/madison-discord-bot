# Madison Discord Bot

## **Available commands**


* **!pic** sends a random picture.


* **!addResponse** adding the message written after the command in the random responses of Madison. ex: **!addResponse Hello World**


* **!gas** returns the current gasPrice on the chain mentionned in your message.

  ex: **!gas ETH** will return the current gasPrice on ETH, in gwei. 
  (Note that you need an API link that returns current gas price.


* **!gasList** returns the list of supported chains for the **!gas** command.


* **!gasAlert** sets a private custom gas alert on any chain that is mentionned in the **!gasList** command. To cancel an alert, set it to 0. You can set 1 alert per chain. 

   ex: **!gasAlert AVAX 50** will trigger an alert as soon as the gasPrice is at 50 gwei on Avax chain, and Madison will notify you. Each alert is sent      once, then reset.
        
* **!myAlerts** check the gas alerts you have set and waiting to be triggered.


* **!save** enables you to save a link in a *json* file. You can save as much links as you want. For privacy reasons, your message will be deleted right after the link is saved.

   ex: **!save https://pbs.twimg.com/media/E3hsoMuVUAMk91Z.jpg**


* **!myLinks** Madison will send you a private message with all your saved links.


* **!deleteLink** Removes a link from your list with its index.

   ex: **!deleteLink 1**


* **!savePic** Enables you to add pictures in Madison folder (*.png* / *.jpg* only).


* **!addCalendar** Create a new calendar in which you can add events.
   ex: **!addCalendar Ethereum**


* **!events** get the saved events of a particular calendar.

   ex: **!events Ethereum** 


* **!calendars** gives you the list of all the registered calendars.


* **!addEvent** add an event in a particular calendar. You must respect the right format. **!addEvent Ethereum, Launch Shitcoin, 13/04**

* **!delEvent** to delete an event from a particular calendar using his number.

   ex: **!delEvent Ethereum 2** will delete the second event in the Ethereum calendar.


* **!allEvents** To get the list of all saved events.

* **Admin Commands: !delResponse, !delCalendar, !deleteLastResponse, !responsesList, !db**

