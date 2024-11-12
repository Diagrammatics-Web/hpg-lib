class ID:
    # used for ID generation
    _id = 0
    @classmethod
    def get_new_id(cls, prefix):
        n_id = prefix + str(cls._id)
        cls._id += 1
        return n_id

    @classmethod
    def reset_id(cls):
        cls._id = 0
