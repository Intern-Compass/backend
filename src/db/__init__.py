from sqlalchemy import MetaData, create_engine, Engine

metadata: MetaData = MetaData()
engine: Engine = create_engine("sqlite:///internship_matching_platform.db")

