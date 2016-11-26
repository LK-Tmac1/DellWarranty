## Dell Warranty Search Web App

####Use case

Search warranty of dell devices from Dell Warranty API by using service tags (svctag).

Service tag is a 7 digits of characters and/or numbers used to identify an dell device. Say DG5QYW1 is Latitude E6430.

1. Input: part of a service tag, say the first 4 are fixed as DG5Q while the last three are unknown. 
2. Output: based on part of a service tag, reterive all dell warranty info of those valid service tags. Then generate an excel file and send the file as an attachment to an email address.

####Challenge: design the workflow

1. How to get all valid service tags?

  Use itertools.product method to generate Cartesian product by using the part svctag. Then use an URL from Dell to check one by one if a svctag is valid or not based on the response from the request with the svctag as parameter.
  
2. How to avoid duplicated work?

  Save the filtered svctag as history record so that next time can be used to find those svctags that are valid in the Cartesian product.
  
3. Exception handling?

  Need to know the error code of response from a request, and take different actions based on different exceptions.
  
4. Resolve the 'utf-8' encoding issue?

  At the top of a py file, add: # -*- coding: utf-8 -*-
  
  Also, reload the sys.setdefaultencoding('utf8').
  

####Reference

More about the searching: http://www.dell.com/support/home/en/cndhs1/Products/?app=warranty

More about the API: http://en.community.dell.com/dell-groups/supportapisgroup/

Python lib used in this project:

1. flask
2. requests
3. xlsxwriter
4. re
5. itertools
6. yaml
