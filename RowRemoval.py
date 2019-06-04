import DB
import itertools
import sys

class RowRemoval:
    def __init__(self, session, parent_row, project_root):
        self.session = session
        self.parent_row = parent_row
        print('parent row')
        print(parent_row)
        self.project_root = project_root
        existing_deletions = set(session.deleted)
        session.delete(parent_row)
        new_deletions = list(set(session.deleted) - existing_deletions)
        self.sorted_deletions = sorted(new_deletions, key=lambda x: x.__tablename__)
    def prompt_user(self):
        for tablename, rows in itertools.groupby(self.sorted_deletions, lambda x: x.__tablename__):
            print('will delete the following rows from: ' + tablename)
            for row in rows:
                print('\t' + (row.identifier() if 'identifier' in dir(row) else str(row)))
        while True:
            response = input('Do you want to make the changes show above? (y/n)')
            if response == 'y':
                break
            elif response == 'n':
                self.session.rollback()
                sys.exit(0)
        self.delete()

    def delete(self):
        for row in self.sorted_deletions:
            if 'remove_files' in dir(row):
                try:
                    row.remove_files(self.project_root)
                except:
                    self.session.rollback()
                    
        self.session.commit()
        
