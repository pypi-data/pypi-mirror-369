!> Tests of get_wavelength
module test_get_wavelength

    ! How to print to stdout
    use ISO_Fortran_env, only: stdout => OUTPUT_UNIT
    use testdrive, only: new_unittest, unittest_type, error_type, check

    use kind_parameters, only: dp

    implicit none
    private

    public :: collect_get_wavelength_tests

contains

    subroutine collect_get_wavelength_tests(testsuite)
        !> Collection of tests
        type(unittest_type), allocatable, intent(out) :: testsuite(:)

        testsuite = [new_unittest("test_get_wavelength_basic", test_get_wavelength_basic)]

    end subroutine collect_get_wavelength_tests

    subroutine test_get_wavelength_basic(error)
        use m_get_wavelength, only: get_wavelength

        type(error_type), allocatable, intent(out) :: error

        real(dp) :: frequency, speed_of_light
        real(dp) :: res, exp

        frequency = 4.3e14_dp
        speed_of_light = 3.0e8_dp

        res = get_wavelength(frequency)

        exp = speed_of_light / frequency

        ! ! How to print to stdout
        ! write( stdout, '(e13.4e2)') res
        ! write( stdout, '(e13.4e2)') exp

        call check(error, res, exp, thr=1.0e-3_dp, rel=.true.)

    end subroutine test_get_wavelength_basic

end module test_get_wavelength
