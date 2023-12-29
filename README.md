# Real-time Image Classifier, Trends Analyzer, and Dataset Creator

This is the project realized for the exam of the subject 'Technologies for Advanced Programming' (University of Catania, Department of Computer Science).

# Architecture

<img src='tap_project_architecture.svg'>

# Disclaimer

<b><h3>This product uses the Flickr API but is not endorsed or certified by SmugMug, Inc.</h3></b>
<h4>I'm not responsible for misuse of this project.</h4>
I also strongly recommend to read the Flickr APIs Terms of Use in order to be aware of what is possible to do and what is not possible to do with Flickr APIs and the data collected through them.

# How to start this project?

1. Set API_KEY and API_SECRET env variables value in 'env' file.
2. Run 'docker compose --env-file env up' command in main folder.
3. Enjoy!
  
# How to query Dataset Creator microservice?

You can use the following url template:  

[http://localhost:8081/getDataset?class=\<class-id\>&max=\<max-urls-to-retrieve\>&min_conf=\<min-confidence-score-the-assigned-class-must-have-to-add-url-in-output-list\>](http://localhost:8081/getDataset?class=\<class-id\>&max=\<max-urls-to-retrieve\>&min_conf=\<min-confidence-score-the-assigned-class-must-have-to-add-url-in-output-list\>)

To get the full list of available class ids visit:

[http://localhost:8081/getClasses](http://localhost:8081/getClasses)<br>

<h4>N.B.</h4>

- Confidence score is a decimal number in [0.0, 1.0].

  - Setting it to a negative number would cause images with whatever class confidence score to be included in the output list.  
  - Setting it to a number greater than 1.0 would lead to an empty output list.

- "class" is a mandatory parameter of the url.
- "max" can be omitted. It defaults to 20.
- "min_conf" can be omitted. It defaults to 0.6.

# How to access Kibana GUI?
  
Simply visit:

http://localhost:5601
