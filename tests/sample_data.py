printable = "".join(chr(i) for i in range(32, 126))

PASSWORDS = ["admin123", "root", "password", printable,
             "very_long_password_to_check_for_character_limit_and_that_it_is_not_the_same_as_in_fill_db_function_"
             "because_it_will_raise_an_error_and_is_this_long_enough_or_it_needs_to_be_longer?"]

USERNAME_WRONG = [""]

USERNAMES_A = ["admin234", "12345", "very_long_name_to_check_for_character_limit_and_that_it_is_not_the_same_as_in_fill"
                                    "_db_function_because_it_will_raise_an_error_and_is_this_long_enough_or_it_needs_to"
                                    "_be_longer"]
USERNAMES_B = ["admin", "123", "test", "very_long_name_to_check_for_character_limit"]

# A != B
USERNAMES = USERNAMES_A + USERNAMES_B
