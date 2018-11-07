  from __future__ import print_function
  from telesign.messaging import MessagingClient
  from telesign.util import random_with_n_digits
  import sys

  if sys.version[0]=="3": raw_input=input
  customer_id = "03A76283-A417-4409-854A-EBAA87E29AA0"
  api_key = "gwSHXLLk0evm669YCttO5QvkMC3KSa6ZoQGKc7V+ZHFst9Z7FFVVW0TjR/BozEIxr3TTyLqUkF4KhImXLciyQg=="

  phone_number = "8618651810182"
  verify_code = random_with_n_digits(5)

  message = "Your code is {}".format(verify_code)
  message_type = "OTP"

  messaging = MessagingClient(customer_id, api_key)
  response = messaging.message(phone_number, message, message_type)

  user_entered_verify_code = raw_input("Please enter the verification code you were sent: ")

  if verify_code == user_entered_verify_code.strip():
      print("Your code is correct.")
  else:
      print("Your code is incorrect.")
  