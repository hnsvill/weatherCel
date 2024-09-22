import unittest, validator

stringSchemaFromMemory = {'type':'string'}
testString = 'hi, im a string.'
class TestValidatorMemorySchema(unittest.TestCase):
    def testValidatesFromMemorySchema(self):
        validatedTestString = validator.validated(
            testString,
            schema=stringSchemaFromMemory
        )
        self.assertEqual(testString,validatedTestString)
    
    def testRaisesWhenMismatchedFromMemorySchema(self):
        # stringSchemaFromMemory = {'type':'string'}
        with self.assertRaises(validator.DataValidationError):
            validator.validated(
                42,
                schema=stringSchemaFromMemory
            )

validators = validator.validatorRegistryFromSchemasDirectory('validatorTestModels')
class TestValidatorValidatorsRegistry(unittest.TestCase):
    def testValidatesFromLoadedValidator(self):
        validatedFromValidatorTestString = validator.validated(
            testString,
            validator=validators['validatorTestString']
        )
        self.assertEqual(testString,validatedFromValidatorTestString)
    
    def testRaisesFromLoadedValidator(self):
        with self.assertRaises(validator.DataValidationError):
            validator.validated(
                42,
                validator=validators['validatorTestString']
            )

    def testValidatesFromLoadedComposedValidator(self):
        testArrayOfStrings = [testString,'another one']
        validatedFromComposedValidatorTestString = validator.validated(
            testArrayOfStrings,
            validator=validators['validatorTestArrayOfStrings']
        )
        self.assertEqual(testArrayOfStrings,validatedFromComposedValidatorTestString)
    
    def testRaisesFromLoadedComposedValidator(self):
        with self.assertRaises(validator.DataValidationError):
            validator.validated(
                [testString,42],
                validator=validators['validatorTestArrayOfStrings']
            )

if __name__ == '__main__':
    unittest.main()