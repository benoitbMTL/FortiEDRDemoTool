import json
import fortiedr

def main():

   organization = "FabricLab" 

   authentication = fortiedr.auth(
      user="apiedr",
      passw="SNDhA85uYx!zZ%4G#GrS^9yYM",
      host="fortinetdemocanada.console.ensilo.com", # use only the hostname, without 'https://' and '/'.
      org=organization         # Case sensitive
   )

   print(authentication['data'])

   admin = fortiedr.Administrator()

   admin_data = admin.list_system_summary(organization=organization)
   
   if admin_data['status']:
      print(json.dumps(admin_data['data'], indent=4))
   

      
if __name__ == "__main__":
    main()