import unittest
import transaction

from pyramid import testing

from shishosan.db import (
    DBSession,
    Base,
)


class BaseModelTestCase(unittest.TestCase):
    def _getTargetClass(self):
        raise NotImplementedError()

    def _makeOne(self):
        raise NotImplementedError()

    def _callFUT(self):
        raise NotImplementedError()

    def setUp(self):
        self.config = testing.setUp()
        self._setup_db()

    def _setup_db(self):
        from sqlalchemy import create_engine
        import shishosan.models  # required for loading model schema

        self.engine = create_engine('sqlite://', echo=True)
        DBSession.configure(bind=self.engine)
        Base.metadata.bind = self.engine
        Base.metadata.create_all(self.engine)

    def tearDown(self):
        DBSession.remove()
        Base.metadata.drop_all(self.engine)

    def _makeUser(self, name='youjo', password='ninja'):
        from shishosan.models import User

        user = User(name, password)
        DBSession.add(user)
        DBSession.flush()
        return user

    def _makeNovel(self, name=u'YouJoの大冒険', pattern_url=r'http://typowriter.org/(\d+).svg'):
        from shishosan.models import Novel

        novel = Novel(name, pattern_url)
        DBSession.add(novel)
        DBSession.flush()
        return novel


class TestUser(BaseModelTestCase):
    def _getTargetClass(self):
        from shishosan.models import User

        return User

    def _makeOne(self, **kwargs):
        return self._getTargetClass()(**kwargs)

    def test_init(self):
        user = self._makeOne(name='ninja', password='raija')
        self.assertEqual(user.name, 'ninja')

    def test_save(self):
        user = self._makeOne(name='ninja', password='raija')

        User = self._getTargetClass()

        self.assertEqual(User.query.count(), 0)

        with transaction.manager:
            DBSession.add(user)

        result_user = User.query.first()
        self.assertEqual(User.query.count(), 1)
        self.assertEqual(result_user.name, 'ninja')

    def test_set_password(self):
        user = self._makeOne(name='ninja', password='raija')

        user.set_password('youjo')

        self.assertFalse(user.verify_password('raija'))
        self.assertTrue(user.verify_password('youjo'))

    def test_verify_password(self):
        user = self._makeOne(name='ninja', password='raija')

        self.assertTrue(user.verify_password('raija'))

    def test_add_bookmark(self):
        pass


class TestNovel(BaseModelTestCase):
    def _getTargetClass(self):
        from shishosan.models import Novel

        return Novel

    def _makeOne(self, **kwargs):
        return self._getTargetClass()(**kwargs)

    def test_init(self):
        novel = self._makeOne(name=u'YouJoの大冒険', pattern_url=r'http://typowriter.org/(\d+).svg')
        self.assertEqual(novel.name, u'YouJoの大冒険')
        self.assertEqual(novel.pattern_url, r'http://typowriter.org/(\d+).svg')

    def test_save(self):
        novel = self._makeOne(name=u'YouJoの大冒険', pattern_url=r'http://typowriter.org/(\d+).svg')

        Novel = self._getTargetClass()
        self.assertEqual(Novel.query.count(), 0)

        with transaction.manager:
            DBSession.add(novel)

        self.assertEqual(Novel.query.count(), 1)

        result_novel = Novel.query.first()
        self.assertEqual(result_novel.name, u'YouJoの大冒険')
        self.assertEqual(result_novel.pattern_url, r'http://typowriter.org/(\d+).svg')


class TestBookmark(BaseModelTestCase):
    def _getTargetClass(self):
        from shishosan.models import Bookmark

        return Bookmark

    def _makeOne(self, **kwargs):
        return self._getTargetClass()(**kwargs)

    def test_init(self):
        user = self._makeUser()
        novel = self._makeNovel()

        bookmark = self._makeOne(user=user, novel=novel)

        self.assertEqual(bookmark.user, user)
        self.assertEqual(bookmark.novel, novel)

    def test_save(self):
        user = self._makeUser()
        novel = self._makeNovel()

        bookmark = self._makeOne(user=user, novel=novel)

        Bookmark = self._getTargetClass()
        self.assertEqual(Bookmark.query.count(), 0)

        with transaction.manager:
            DBSession.add(bookmark)

        self.assertEqual(Bookmark.query.count(), 1)
