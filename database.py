from functools import total_ordering
import psycopg2
import psycopg2.extras
from util import parse_config

# standard database connection used by both services
def connect():
    config = parse_config('database')
    conn = psycopg2.connect(host=config['host'],
                            port=config['port'],
                            database=config['database'],
                            user=config['user'],
                            password=config['password'] if 'password' in config else None)
    return conn

conn = connect()


class PlaceProject:

    @staticmethod
    def create_table():
        command = '''
            CREATE TABLE IF NOT EXISTS PlaceProjects ( 
            name text PRIMARY KEY,
            total bigint,
            placed bigint
        );'''

        cur = conn.cursor()
        cur.execute(command)
        conn.commit()
        cur.close()

    @staticmethod
    def delete_table():
        command = '''
            DROP TABLE IF EXISTS PlaceProjects CASCADE;
        '''

        cur = conn.cursor()
        cur.execute(command)
        conn.commit()
        cur.close()

    def __init__(self, name, total, placed):
        self.name = name
        self.total = total
        self.placed = placed

    @staticmethod
    def create_from_row(row):
        if row is None:
            return None
        name, total, placed = row
        return PlaceProject(name, total, placed)

    @staticmethod
    def get_by_name(name):
        cur = conn.cursor()
        command = '''SELECT * FROM PlaceProjects WHERE name = %s'''
        cur.execute(command, (name,))
        row = cur.fetchone()
        cur.close()

        if row is None:
            return None

        return PlaceProject.create_from_row(row)

    @staticmethod
    def get_all():
        cur = conn.cursor()
        command = '''SELECT * FROM PlaceProjects;'''
        cur.execute(command)
        rows = cur.fetchall()
        cur.close()

        return [PlaceProject.create_from_row(row) for row in rows]

    def insert(self):
        cur = conn.cursor()
        command = '''INSERT INTO PlaceProjects(
        name,
        total,
        placed
        ) 
        VALUES (%s, %s, %s);'''

        cur.execute(command,
        (
        self.name,
        self.total,
        self.placed
        ))

        conn.commit()
        cur.close()

    def get_pixels(self):
        cur = conn.cursor()
        command = '''SELECT * FROM PlacePixels WHERE project = %s'''

        cur.execute(command, (self.id,))
        rows = cur.fetchall()
        cur.close()

        return [PlacePixel.create_from_row(row) for row in rows]

    def update(self):
        cur = conn.cursor()
        command = '''UPDATE PlaceProjects
        SET
        total = %s,
        placed = %s
        WHERE name = %s
        '''

        cur.execute(command,
        (
        self.total,
        self.placed,
        self.name
        ))

        conn.commit()
        cur.close()

    def delete(self):
        cur = conn.cursor()
        command = '''DELETE FROM PlaceProjects WHERE name = %s'''
        cur.execute(command,(self.name, ))
        conn.commit()
        cur.close()


class PlacePixel:

    @staticmethod
    def create_table():
        command = '''
            CREATE TABLE IF NOT EXISTS PlacePixels ( 
            id SERIAL PRIMARY KEY,
            project text REFERENCES PlaceProjects(name) ON DELETE CASCADE,
            x int,
            y int,
            color text
        );'''

        cur = conn.cursor()
        cur.execute(command)
        conn.commit()
        cur.close()

    @staticmethod
    def delete_table():
        command = '''
            DROP TABLE IF EXISTS PlacePixels CASCADE;
        '''

        cur = conn.cursor()
        cur.execute(command)
        conn.commit()
        cur.close()

    def __init__(self, id, project, x, y, color):
        self.id = id
        self.project = project
        self.x = x
        self.y = y
        self.color = color

    @staticmethod
    def create_from_row(row):
        if row is None:
            return None
        id, project, x, y, color = row
        return PlacePixel(id, project, x, y, color)

    @staticmethod
    def get(id):
        cur = conn.cursor()
        command = '''SELECT * FROM PlacePixels WHERE id = %s'''
        cur.execute(command, (id,))
        row = cur.fetchone()
        cur.close()

        if row is None:
            return None

        return PlacePixel.create_from_row(row)

    @staticmethod
    def get_random():
        cur = conn.cursor()
        command = '''SELECT * FROM PlacePixels'''
        cur.execute(command)
        row = cur.fetchone()
        cur.close()

        if row is None:
            return None

        return PlacePixel.create_from_row(row)

    @staticmethod
    def insert_pixels(pixels):
        cur = conn.cursor()
        command = '''INSERT INTO PlacePixels(
        project,
        x,
        y,
        color
        ) 
        VALUES (%s, %s, %s, %s);'''

        formatted_pixels = []
        for p in pixels:
            formatted_pixels.append(
                (
                    p.project,
                    p.x,
                    p.y,
                    p.color
                )
            )
        
        psycopg2.extras.execute_batch(cur, command, formatted_pixels)
        conn.commit()
        cur.close()


    def insert(self):
        cur = conn.cursor()
        command = '''INSERT INTO PlacePixels(
        project,
        x,
        y,
        color
        ) 
        VALUES (%s, %s, %s, %s);'''

        cur.execute(command,
        (
        self.project,
        self.x,
        self.y,
        self.color
        ))

        conn.commit()
        cur.close()

    def delete(self):
        cur = conn.cursor()
        command = '''DELETE FROM PlacePixels WHERE id = %s'''
        cur.execute(command,(self.id, ))
        conn.commit()
        cur.close()


conn = connect()