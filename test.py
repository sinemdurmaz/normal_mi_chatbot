from masker import mask_text

user_message = input("Şikayetinizi yazınız:\n")

print("\nTemizlenmiş Veri:\n")
print(mask_text(user_message))