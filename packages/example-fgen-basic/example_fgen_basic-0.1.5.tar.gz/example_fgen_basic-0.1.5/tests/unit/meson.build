testdrive_dep = dependency(
  'test-drive',
  fallback: ['test-drive', 'testdrive_dep'],
  default_options: ['default_library=static'],
  static: true,
)

test_file_stubs = [
  'test_get_wavelength',
]

test_srcs = files(
  'main.f90',
)
foreach test_file_stub : test_file_stubs
  test_srcs += files('@0@.f90'.format(test_file_stub))
endforeach

unit_tester = executable(
  '@0@-tester-unit'.format(meson.project_name()),
  sources: test_srcs,
  dependencies: [example_dep, testdrive_dep],
)

foreach test_file_stub : test_file_stubs
  test(
    'unit_@0@'.format(test_file_stub),
    unit_tester,
    args: [test_file_stub],
  )
endforeach
