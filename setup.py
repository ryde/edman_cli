from setuptools import setup

setup(
    entry_points={
            'console_scripts': [
                'ed_assign_bson_type=scripts.assign_bson_type:main',
                'ed_db_create=scripts.db_create:main',
                'ed_db_destroy=scripts.db_destroy:main',
                'ed_delete=scripts.delete:main',
                'ed_entry=scripts.entry:main',
                'ed_file_add=scripts.file_add:main',
                'ed_file_delete=scripts.file_delete:main',
                'ed_file_dl=scripts.file_dl:main',
                'ed_find=scripts.find:main',
                'ed_item_delete=scripts.item_delete:main',
                'ed_pullout=scripts.pullout:main',
                'ed_structure_convert=scripts.structure_convert:main',
                'ed_update=scripts.update:main',
            ],
        },

)
