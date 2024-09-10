"""To może się przydać i w test_db oraz w test_api."""

printable_ascii: str = "".join(chr(i) for i in range(32, 126))
printable_utf8_1: str = "".join(chr(i) for i in range(160, 200))
printable_utf8_2: str = "".join(chr(i) for i in range(200, 255))

PASSWORDS: list[str] = ["admin123", "root", "password", printable_ascii, printable_utf8_1, printable_utf8_2,
                        "very_long_password_to_check_for_character_limit_and_that_it_is_not_the_same_as_in_fill_db_"
                        "function_because_it_will_raise_an_error_and_is_this_long_enough_or_it_needs_to_be_longer?"]

USERNAME_WRONG: list[str] = [""]

USERNAMES_A: list[str] = ["admin234", "12345",
                          "very_long_name_to_check_for_character_limit_and_that_it_is_not_the_same_as_in_fill_db_"
                          "function_because_it_will_raise_an_error_and_is_this_long_enough_or_it_needs_to_be_longer"]
USERNAMES_B: list[str] = ["admin", "123", "test", "very_long_name_to_check_for_character_limit"]

# it is required to USERNAMES_A != USERNAMES_B
USERNAMES: list[str] = USERNAMES_A + USERNAMES_B
