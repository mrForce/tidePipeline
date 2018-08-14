import DB
import itertools


class RowRemoval:
    def __init__(self, session, parent_row, project_root):
        self.session = session
        self.parent_row = parent_row
        self.project_root = project_root
        existing_deletions = set(session.deleted)
        session.delete(parent_row)
        new_deletions = list(set(session.deleted) - existing_deletions)
        self.sorted_deletions = sorted(new_deletions, key=lambda x: x.__tablename__)
    def get_deletion_message(self):
        lines = []
        for tablename, rows in itertools.groupby(self.sorted_deletions, lambda x: x.__tablename__):
            lines.append('will delete the following rows from: ' + tablename)
            for row in rows:
                lines.append('\t' + (row.identifier() if 'identifier' in dir(row) else str(row)))
        return '\n'.join(lines)

    def delete(self):
        for row in self.sorted_deletions:
            if 'remove_files' in dir(row):
                row.remove_files(self.project_root)
        self.session.commit()
        
