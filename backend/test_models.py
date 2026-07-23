import unittest
from app import app
from database import db
from models import (
    User, Role, Module, RoleMapping,
    Profile, Application, InternshipSchedule,
    BankDetails, Document, Review, Approval
)
from datetime import date, datetime

class Milestone2ModelsValidationTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = app
        cls.app_context = cls.app.app_context()
        cls.app_context.push()
        db.create_all()

    @classmethod
    def tearDownClass(cls):
        db.session.remove()
        cls.app_context.pop()

    def setUp(self):
        db.session.begin_nested()

    def tearDown(self):
        db.session.rollback()

    def test_01_verify_model_imports(self):
        """1. Verify Model Imports for all 11 required tables"""
        model_classes = [
            Role, Module, RoleMapping, User, Profile,
            InternshipSchedule, Application, BankDetails,
            Document, Review, Approval
        ]
        for model in model_classes:
            self.assertTrue(hasattr(model, "__tablename__"))
            self.assertIsNotNone(model.__tablename__)
        print("\n[PASS] 1. Verified imports for all 11 SQLAlchemy models.")

    def test_02_role_mapping_relationships(self):
        """2. Verify Role, Module, and RoleMapping relationships"""
        role = Role(role_name="Applicant", description="Applicant role")
        module = Module(module_id="MOD_APPLICATIONS", module_name="Applications", description="Applications Module")
        db.session.add_all([role, module])
        db.session.flush()

        role_map = RoleMapping(role_id=role.id, module_id=module.id, can_read=True, can_update=True, can_delete=False)
        db.session.add(role_map)
        db.session.flush()

        self.assertEqual(len(role.mappings), 1)
        self.assertEqual(role.mappings[0].module.module_name, "Applications")
        self.assertTrue(role.mappings[0].can_read)
        print("[PASS] 2. Role Mapping relationships (Role -> RoleMapping -> Module) verified.")

    def test_03_user_profile_one_to_one(self):
        """3. Verify One-to-One relationship: User -> Profile"""
        role = Role(role_name="ApplicantRole")
        module = Module(module_name="ProfilesMod")
        db.session.add_all([role, module])
        db.session.flush()

        role_map = RoleMapping(role_id=role.id, module_id=module.id, can_read=True)
        db.session.add(role_map)
        db.session.flush()

        user = User(email="test_user@iitm.ac.in", username="user_test", role_mapping_id=role_map.id)
        db.session.add(user)
        db.session.flush()

        profile = Profile(user_id=user.id, full_name="Test Applicant Name", department="CSE", register_number="CS1001")
        db.session.add(profile)
        db.session.flush()

        self.assertIsNotNone(user.profile)
        self.assertEqual(user.profile.full_name, "Test Applicant Name")
        self.assertEqual(profile.user.email, "test_user@iitm.ac.in")
        print("[PASS] 3. One-to-One relationship (User -> Profile) verified.")

    def test_04_profile_applications_one_to_many(self):
        """4. Verify One-to-Many relationship: Profile -> Applications"""
        role = Role(role_name="ApplicantRole2")
        module = Module(module_name="AppsMod")
        db.session.add_all([role, module])
        db.session.flush()

        role_map = RoleMapping(role_id=role.id, module_id=module.id, can_read=True)
        db.session.add(role_map)
        db.session.flush()

        user = User(email="applicant_multi@iitm.ac.in", username="applicant_multi", role_mapping_id=role_map.id)
        db.session.add(user)
        db.session.flush()

        profile = Profile(user_id=user.id, full_name="Multi Application Student")
        db.session.add(profile)
        db.session.flush()

        app1 = Application(profile_id=profile.id, application_number="APP-2026-001", status="DRAFT")
        app2 = Application(profile_id=profile.id, application_number="APP-2026-002", status="SUBMITTED")
        db.session.add_all([app1, app2])
        db.session.flush()

        self.assertEqual(len(profile.applications), 2)
        self.assertEqual(app1.profile.full_name, "Multi Application Student")
        print("[PASS] 4. One-to-Many relationship (Profile -> Applications) verified.")

    def test_05_application_bank_details_one_to_one(self):
        """5. Verify One-to-One relationship: Application -> Bank Details"""
        user = User(email="bank_test@iitm.ac.in", role_mapping_id=1)
        role = Role(role_name="BankRole")
        module = Module(module_name="BankMod")
        db.session.add_all([role, module])
        db.session.flush()

        role_map = RoleMapping(role_id=role.id, module_id=module.id)
        db.session.add(role_map)
        db.session.flush()
        user.role_mapping_id = role_map.id
        db.session.add(user)
        db.session.flush()

        profile = Profile(user_id=user.id, full_name="Bank Test Student")
        db.session.add(profile)
        db.session.flush()

        app_obj = Application(profile_id=profile.id, application_number="APP-BANK-01")
        db.session.add(app_obj)
        db.session.flush()

        bank = BankDetails(
            application_id=app_obj.id,
            account_holder_name="Bank Test Student",
            bank_name="Canara Bank",
            account_number="987654321",
            ifsc_code="CNRB0001234"
        )
        db.session.add(bank)
        db.session.flush()

        self.assertIsNotNone(app_obj.bank_details)
        self.assertEqual(app_obj.bank_details.bank_name, "Canara Bank")
        self.assertEqual(bank.application.application_number, "APP-BANK-01")
        print("[PASS] 5. One-to-One relationship (Application -> Bank Details) verified.")

    def test_06_application_documents_one_to_many(self):
        """6. Verify One-to-Many relationship: Application -> Documents"""
        role = Role(role_name="DocRole")
        module = Module(module_name="DocMod")
        db.session.add_all([role, module])
        db.session.flush()

        role_map = RoleMapping(role_id=role.id, module_id=module.id)
        db.session.add(role_map)
        db.session.flush()

        user = User(email="doc_test@iitm.ac.in", role_mapping_id=role_map.id)
        db.session.add(user)
        db.session.flush()

        profile = Profile(user_id=user.id, full_name="Doc Student")
        db.session.add(profile)
        db.session.flush()

        app_obj = Application(profile_id=profile.id, application_number="APP-DOC-01")
        db.session.add(app_obj)
        db.session.flush()

        doc1 = Document(application_id=app_obj.id, document_type="RESUME", file_name="resume.pdf", file_path="uploads/resume.pdf")
        doc2 = Document(application_id=app_obj.id, document_type="NOC", file_name="noc.pdf", file_path="uploads/noc.pdf")
        db.session.add_all([doc1, doc2])
        db.session.flush()

        self.assertEqual(len(app_obj.documents), 2)
        self.assertEqual(doc1.application.application_number, "APP-DOC-01")
        print("[PASS] 6. One-to-Many relationship (Application -> Documents) verified.")

    def test_07_reviews_approvals_relationships(self):
        """7. Verify relationships for Reviews and Approvals"""
        role = Role(role_name="ReviewRole")
        module = Module(module_name="ReviewMod")
        db.session.add_all([role, module])
        db.session.flush()

        role_map = RoleMapping(role_id=role.id, module_id=module.id)
        db.session.add(role_map)
        db.session.flush()

        supervisor = User(email="supervisor@iitm.ac.in", role_mapping_id=role_map.id)
        chairman = User(email="chairman@iitm.ac.in", role_mapping_id=role_map.id)
        applicant = User(email="applicant_rev@iitm.ac.in", role_mapping_id=role_map.id)
        db.session.add_all([supervisor, chairman, applicant])
        db.session.flush()

        profile = Profile(user_id=applicant.id, full_name="Applicant Under Review")
        db.session.add(profile)
        db.session.flush()

        app_obj = Application(profile_id=profile.id, application_number="APP-REV-01")
        db.session.add(app_obj)
        db.session.flush()

        review = Review(application_id=app_obj.id, supervisor_id=supervisor.id, recommendation="RECOMMENDED", remarks="Strong candidate")
        approval = Approval(application_id=app_obj.id, chairman_id=chairman.id, decision="APPROVED", comments="Approved for internship")
        db.session.add_all([review, approval])
        db.session.flush()

        self.assertEqual(len(app_obj.reviews), 1)
        self.assertEqual(app_obj.reviews[0].supervisor.email, "supervisor@iitm.ac.in")
        self.assertEqual(len(app_obj.approvals), 1)
        self.assertEqual(app_obj.approvals[0].chairman.email, "chairman@iitm.ac.in")
        print("[PASS] 7. Reviews and Approvals relationships verified.")

if __name__ == "__main__":
    print("Running Milestone 2 Model Validation & Verification Suite...")
    unittest.main()
