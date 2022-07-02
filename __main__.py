import filtered_stream
def main():
    rules = filtered_stream.get_rules()
    delete = filtered_stream.delete_all_rules(rules)
    set = filtered_stream.set_rules(delete)
    filtered_stream.get_stream(set)
   

if __name__ == "__main__":
    main()
