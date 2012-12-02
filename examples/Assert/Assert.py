class Assert:
    '''
    This example shows the usage of the assert
    assert_equal :
    -------------
    utilities.assert_equals(expect=1,actual=1,
          onpass="Expected result equal to Actual",
          onfail="Expected result not equal to Actual") 
    
    assert_matches:
    --------------
    expect = "Res(.*)"
    actual = "Result : Test Passed"
    utilities.assert_equals(expect=expect,actual=actual,
              onpass="Expected result matches with Actual",
              onfail="Expected result didn't matched with Actual")
    
    assert_greater:
    --------------
    expect = 10
            actual = 5
            utilities.assert_greater(expect=expect,actual=actual,
                  onpass=str(expect)+" greater than the "+str(actual),
                  onfail=str(expect)+" is not greater than "+str(actual))
    
    assert_lesser:
    -------------
    expect = 5
            actual = 10
            utilities.assert_lesser(expect=expect,actual=actual,
                     onpass=str(expect)+" is lesser than the "+str(actual),
                     onfail=str(expect)+" is not lesser than the "+str(actual))
                     
    
    cd ~/bin/
    ./launcher --example Assert 
       will execute this example.
    '''
    def __init__(self):
        self.default = ""
                
    def CASE1(self, main):
        '''
        This test case will showcase usage of assert to verify the result
        '''
        
        main.case("Using assert to verify the result ")
        main.step("Using assert_equal to verify the result is equivalent or not")
        expect = main.TRUE
        actual = main.TRUE
        utilities.assert_equals(expect=expect, actual=actual, onpass=str(expect) + " is equal to " + str(actual), onfail=str(expect) + " is not equal to " + str(actual)) 

        main.step("Using assert_matches to verify the result matches or not")
        expect = "Res(.*)"
        actual = "Result"
        utilities.assert_matches(expect=expect, actual=actual, onpass=expect + " is matches to " + actual, onfail=expect + " is not matching with " + actual)
        
        main.step("Using assert_greater to verify the result greater or not")
        expect = 10
        actual = 5
        utilities.assert_greater(expect=expect, actual=actual, onpass=str(expect) + " greater than the " + str(actual), onfail=str(expect) + " is not greater than " + str(actual))
        
        main.step("Using assert_greater to verify the result lesser or not")
        expect = 5
        actual = 10
        utilities.assert_lesser(expect=expect, actual=actual, onpass=str(expect) + " is lesser than the " + str(actual), onfail=str(expect) + " is not lesser than the " + str(actual))
